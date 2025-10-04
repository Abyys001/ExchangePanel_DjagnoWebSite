from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import datetime
import logging

from .forms import CategoryForm, PriceTypeFormSet
from .models import Category, PriceType, Price

logger = logging.getLogger(__name__)

@login_required
def create_category(request):
    """
    Handle creation of a new Category and its related PriceTypes.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        formset = PriceTypeFormSet(request.POST)
        
        try:
            if form.is_valid() and formset.is_valid():
                with transaction.atomic():
                    category = form.save()
                    price_types = formset.save(commit=False)
                    for price_type in price_types:
                        price_type.category = category
                        price_type.save()
                    
                messages.success(request, f'Category "{category.name}" created successfully!')
                logger.info(f'Category "{category.name}" created by user {request.user.username}')
                return redirect('pricing:category_list')
        except ValidationError as e:
            messages.error(request, f'Validation error: {str(e)}')
            logger.error(f'Validation error in create_category: {str(e)}')
        except Exception as e:
            messages.error(request, 'An error occurred while creating the category.')
            logger.error(f'Error in create_category: {str(e)}')
    else:
        form = CategoryForm()
        formset = PriceTypeFormSet()

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'pricing/category_form.html', context)

@login_required
def category_list(request):
    """
    Display a list of all categories with their related price types and prices.
    """
    categories = Category.objects.prefetch_related(
        'price_types', 'price_types__prices'
    ).order_by('-created_at').all()

    context = {
        'categories': categories
    }
    return render(request, 'pricing/category_list.html', context)

@login_required
def delete_category(request, pk):
    """
    Delete a category by its primary key directly (called from list view).
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('pricing:category_list')
    
    category = get_object_or_404(Category, pk=pk)
    category_name = category.name
    
    try:
        with transaction.atomic():
            category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        logger.info(f'Category "{category_name}" deleted by user {request.user.username}')
    except Exception as e:
        messages.error(request, 'An error occurred while deleting the category.')
        logger.error(f'Error deleting category {pk}: {str(e)}')
    
    return redirect('pricing:category_list') 

@login_required
def edit_category(request, pk):
    """
    Handle editing of an existing Category and its related PriceTypes.
    """
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        formset = PriceTypeFormSet(request.POST, instance=category)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('pricing:category_list')
    else:
        form = CategoryForm(instance=category)
        formset = PriceTypeFormSet(instance=category)

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'pricing/category_form.html', context)

@login_required
def price_list(request):
    price_types = PriceType.objects.select_related('category').prefetch_related('prices')
    price_data = []

    for pt in price_types:
        current_price_obj = pt.prices.filter(is_current=True).first()
        price_data.append({
            'category': pt.category,
            'price_type': pt,
            'current_price': current_price_obj.price if current_price_obj else 'N/A',
            'last_updated': current_price_obj.updated_at if current_price_obj else None,
            'slug': pt.category.slug  # اضافه کردن slug
        })

    context = {
        'price_data': price_data,
        'price_types': price_types,
        'categories': set(pt.category for pt in price_types),
        'active_prices_count': sum(1 for pt in price_types if pt.prices.filter(is_current=True).exists()),
        'today_updates_count': sum(
            1 for pt in price_types if pt.prices.filter(is_current=True, updated_at__date=datetime.date.today()).exists()
        ),
    }

    return render(request, 'pricing/price_list.html', context)

@login_required
def category_prices_form(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    if request.method == "POST":
        updated_count = 0
        error_count = 0
        
        try:
            with transaction.atomic():
                for price_type in category.price_types.all():
                    price_field = f'price_{price_type.id}'
                    new_price_value = request.POST.get(price_field)
                    
                    if new_price_value:
                        try:
                            new_price = Decimal(new_price_value.strip())
                            if new_price <= 0:
                                raise ValueError("Price must be greater than zero")
                                
                            current_price = price_type.get_current_price_object()
                            
                            # اگر قیمت تغییر کرده یا قیمت جاری وجود ندارد
                            if current_price is None or new_price != current_price.price:
                                # ایجاد یا به‌روزرسانی قیمت از طریق مدل
                                if current_price:
                                    # به‌روزرسانی قیمت موجود
                                    current_price.price = new_price
                                    current_price.save()
                                else:
                                    # ایجاد قیمت جدید
                                    Price.objects.create(
                                        price_type=price_type,
                                        price=new_price,
                                        is_current=True
                                    )
                                updated_count += 1
                        except (ValueError, TypeError, InvalidOperation) as e:
                            error_count += 1
                            messages.error(request, f"Invalid price for {price_type.name}: {str(e)}")
                            logger.warning(f'Invalid price input for {price_type.name}: {new_price_value}')
                
                if updated_count > 0:
                    messages.success(request, f"Successfully updated {updated_count} price(s)!")
                    logger.info(f'Updated {updated_count} prices for category {category.name} by user {request.user.username}')
                
                if error_count > 0:
                    messages.warning(request, f"{error_count} price(s) had errors and were not updated.")
                    
        except Exception as e:
            messages.error(request, "An error occurred while updating prices.")
            logger.error(f'Error updating prices for category {category_slug}: {str(e)}')
        
        return redirect("pricing:price_list")

    context = {
        "category": category,
    }
    return render(request, "pricing/price_form.html", context)