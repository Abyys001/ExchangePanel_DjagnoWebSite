from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import CategoryForm, PriceTypeFormSet
from .models import Category, PriceType, Price
from django.utils import timezone
import datetime
from django.contrib import messages
from decimal import Decimal

@login_required
def create_category(request):
    """
    Handle creation of a new Category and its related PriceTypes.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        formset = PriceTypeFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            category = form.save()
            price_types = formset.save(commit=False)
            for price_type in price_types:
                price_type.category = category
                price_type.save()
            return redirect('pricing:category_list')
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
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('pricing:category_list')
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
        for price_type in category.price_types.all():
            price_field = f'price_{price_type.id}'
            new_price_value = request.POST.get(price_field)
            
            if new_price_value:
                try:
                    new_price = Decimal(new_price_value)
                    current_price = price_type.get_current_price_object()
                    
                    # اگر قیمت تغییر کرده یا قیمت جاری وجود ندارد
                    if current_price is None or new_price != current_price.price:
                        # ایجاد یا به‌روزرسانی قیمت از طریق مدل
                        if current_price:
                            # به‌روزرسانی قیمت موجود (که سیگنال را فعال می‌کند)
                            current_price.price = new_price
                            current_price.save()
                        else:
                            # ایجاد قیمت جدید
                            Price.objects.create(
                                price_type=price_type,
                                price=new_price,
                                is_current=True
                            )
                except (ValueError, TypeError):
                    messages.error(request, f"Invalid price for {price_type.name}")
        
        messages.success(request, "Prices updated successfully!")
        return redirect("pricing:price_list")

    context = {
        "category": category,
    }
    return render(request, "pricing/price_form.html", context)