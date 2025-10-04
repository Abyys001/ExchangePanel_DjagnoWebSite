from django import forms
from django.forms import inlineformset_factory
from .models import Category, PriceType, Price


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if not name:
                raise forms.ValidationError("Category name cannot be empty.")
        return name


class PriceTypeForm(forms.ModelForm):
    class Meta:
        model = PriceType
        fields = ['name', 'action', 'base_currency', 'target_currency', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Buy USDT with IRR'}),
            'action': forms.Select(attrs={'class': 'form-select'}),
            'base_currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. USDT'}),
            'target_currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. IRR'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        base_currency = cleaned_data.get('base_currency')
        target_currency = cleaned_data.get('target_currency')
        
        if base_currency and target_currency and base_currency == target_currency:
            raise forms.ValidationError("Base and target currencies cannot be the same.")
        
        return cleaned_data


class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['price', 'is_current']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price


# ایجاد یک InlineFormset برای PriceType مرتبط با Category
PriceTypeFormSet = inlineformset_factory(
    Category,  # والد
    PriceType,  # فرزند
    form=PriceTypeForm,
    extra=1,  # چند فرم خالی در ابتدا نشان داده شود
    can_delete=True  # اجازه حذف PriceType از همان فرم
)
