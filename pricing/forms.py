from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Category, PriceType, Price


class PriceTypeFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # علامت‌گذاری برای جلوگیری از بازگشت
        self._adding_fields = False

    def clean(self):
        """Remove empty forms from validation"""
        super().clean()
        
        # Remove empty forms from validation
        for form in self.forms:
            if self._is_form_empty(form) and not form.cleaned_data.get('DELETE', False):
                form.cleaned_data = {}
    
    def _is_form_empty(self, form):
        """Check if a form is completely empty"""
        # Check all fields except DELETE
        for field_name in form.fields:
            if field_name != 'DELETE' and form.cleaned_data.get(field_name):
                return False
        return True
    
    def add_fields(self, form, index):
        """Add fields with custom validation"""
        # جلوگیری از بازگشت بی‌نهایت
        if hasattr(self, '_adding_fields') and self._adding_fields:
            return
            
        self._adding_fields = True
        
        try:
            # فراخوانی متد والد اصلی
            super(BaseInlineFormSet, self).add_fields(form, index)
            
            # Make fields not required for extra forms (new empty forms)
            # بررسی کنید که index None نباشد (برای empty_form)
            if index is not None and index >= len(self.initial_forms):
                for field_name in ['name', 'action', 'base_currency', 'target_currency']:
                    if field_name in form.fields:
                        form.fields[field_name].required = False
        finally:
            self._adding_fields = False
    
    def save(self, commit=True):
        """Save only non-empty forms"""
        instances = super().save(commit=False)
        
        # Filter out empty forms
        non_empty_instances = []
        for instance in instances:
            # Check if instance has any data (excluding auto fields)
            if (instance.name or instance.base_currency or 
                instance.target_currency or instance.description):
                non_empty_instances.append(instance)
        
        if commit:
            for instance in non_empty_instances:
                instance.save()
            self.save_m2m()
        
        return non_empty_instances


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
            
            # Check for unique name (excluding current instance for edit)
            if self.instance.pk:
                if Category.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("A category with this name already exists.")
            else:
                if Category.objects.filter(name=name).exists():
                    raise forms.ValidationError("A category with this name already exists.")
                    
        return name


class PriceTypeForm(forms.ModelForm):
    class Meta:
        model = PriceType
        fields = ['name', 'action', 'base_currency', 'target_currency', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Buy USDT with IRR'
            }),
            'action': forms.Select(attrs={
                'class': 'form-select'
            }),
            'base_currency': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. USDT'
            }),
            'target_currency': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. IRR'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Optional description'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # برای فرم‌های جدید، فیلدها را غیرالزامی کن
        if not self.instance.pk:
            for field_name in ['name', 'action', 'base_currency', 'target_currency']:
                if field_name in self.fields:
                    self.fields[field_name].required = False

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if not name:
                raise forms.ValidationError("Price type name cannot be empty.")
        return name

    def clean_base_currency(self):
        base_currency = self.cleaned_data.get('base_currency')
        if base_currency:
            base_currency = base_currency.strip().upper()
            if not base_currency:
                raise forms.ValidationError("Base currency cannot be empty.")
        return base_currency

    def clean_target_currency(self):
        target_currency = self.cleaned_data.get('target_currency')
        if target_currency:
            target_currency = target_currency.strip().upper()
            if not target_currency:
                raise forms.ValidationError("Target currency cannot be empty.")
        return target_currency

    def clean(self):
        cleaned_data = super().clean()
        
        # Skip validation for empty forms
        name = cleaned_data.get('name')
        base_currency = cleaned_data.get('base_currency')
        target_currency = cleaned_data.get('target_currency')
        
        # If all required fields are empty, skip further validation
        if not name and not base_currency and not target_currency:
            return cleaned_data
        
        # Only validate if at least one field is filled
        if base_currency and target_currency and base_currency == target_currency:
            raise forms.ValidationError("Base and target currencies cannot be the same.")
        
        # Check for unique price type name within the same category
        category = self.instance.category if self.instance.pk else None
        
        if name and category:
            # For existing instances (edit)
            if self.instance.pk:
                if PriceType.objects.filter(
                    category=category, 
                    name=name
                ).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError(
                        "A price type with this name already exists in this category."
                    )
            # For new instances (create)
            elif PriceType.objects.filter(category=category, name=name).exists():
                raise forms.ValidationError(
                    "A price type with this name already exists in this category."
                )
        
        return cleaned_data


class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['price', 'is_current']
        widgets = {
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'min': '0'
            }),
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
    formset=PriceTypeFormSet,  # Use custom formset
    extra=1,  # چند فرم خالی در ابتدا نشان داده شود
    can_delete=True,  # اجازه حذف PriceType از همان فرم
    fields=['name', 'action', 'base_currency', 'target_currency', 'description', 'is_active'],
)