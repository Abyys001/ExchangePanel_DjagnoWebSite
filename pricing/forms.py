from django import forms
from django.forms import inlineformset_factory
from .models import Category, PriceType

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']

class PriceTypeForm(forms.ModelForm):
    class Meta:
        model = PriceType
        fields = ['name', 'action', 'base_currency', 'target_currency', 'description', 'is_active']

# ایجاد یک InlineFormset برای PriceType مرتبط با Category
PriceTypeFormSet = inlineformset_factory(
    Category,  # والد
    PriceType,  # فرزند
    form=PriceTypeForm,
    extra=1,  # چند فرم خالی در ابتدا نشان داده شود
    can_delete=True  # اجازه حذف PriceType از همان فرم
)

from django import forms
from .models import Price, PriceType

# pricing/forms.py
from django import forms
from .models import Price

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['price', 'is_current']  # فقط فیلدهایی که می‌خواهید ویرایش شوند
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
