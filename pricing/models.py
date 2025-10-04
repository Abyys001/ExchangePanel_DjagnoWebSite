from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Category(models.Model):
    """
    Categories like Tether, Bitcoin, etc.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError("Category name cannot be empty.")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

class PriceType(models.Model):
    """
    Buy/Sell types within a category
    (e.g., Buy Tether to Rial, Sell Tether to Bond)
    """
    ACTION_CHOICES = [
        ("buy", "Buy"),
        ("sell", "Sell"),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="price_types")
    name = models.CharField(max_length=200)  # e.g., "Buy Tether to Rial"
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    base_currency = models.CharField(max_length=20)  # e.g., "Tether"
    target_currency = models.CharField(max_length=20)  # e.g., "Rial"
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def get_current_price(self):
        """Return the current price value or 0 if not found"""
        current_price = self.prices.filter(is_current=True).first()
        return current_price.price if current_price else 0
    
    def get_current_description(self):
        """Return the current price description or empty string if not found"""
        current_price = self.prices.filter(is_current=True).first()
        return current_price.description if current_price else ""
    
    def get_current_price_object(self):
        """Return the current price object or None if not found"""
        return self.prices.filter(is_current=True).first()

    class Meta:
        ordering = ["category__name", "action", "name"]
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_price_type_name_per_category")
        ]


class Price(models.Model):
    """
    Current and historical prices for a specific PriceType.
    Only one price can be current per PriceType.
    """
    price_type = models.ForeignKey(PriceType, on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=20, decimal_places=4)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # اگر این یک قیمت جدید است یا قیمت تغییر کرده
        if self.pk:  # Existing instance
            old_instance = Price.objects.get(pk=self.pk)
            if old_instance.price != self.price and self.is_current:
                # ایجاد رکورد تاریخچه
                PriceHistory.objects.create(
                    price_type=self.price_type,
                    old_price=old_instance.price,
                    new_price=self.price,
                    change_percentage=((self.price - old_instance.price) / old_instance.price) * 100 if old_instance.price != 0 else 0,
                    changed_at=timezone.now(),
                    notes=f"Price updated from {old_instance.price} to {self.price}"
                )
        
        # Ensure only one current price per PriceType
        if self.is_current:
            Price.objects.filter(price_type=self.price_type, is_current=True).exclude(pk=self.pk).update(is_current=False)
        
        super().save(*args, **kwargs)

    def clean(self):
        if self.price <= 0:
            raise ValidationError("Price must be greater than zero.")

        if self.price_type.base_currency == self.price_type.target_currency:
            raise ValidationError("Base and target currencies cannot be the same.")
        
        # Ensure only one current price per PriceType
        if self.is_current:
            existing_current = Price.objects.filter(
                price_type=self.price_type, 
                is_current=True
            ).exclude(pk=self.pk).exists()
            if existing_current:
                raise ValidationError("Only one current price is allowed per price type.")

    def __str__(self):
        return f"{self.price_type.name}: {self.price}"

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["price_type", "is_current"],
                condition=models.Q(is_current=True),
                name="unique_current_price_per_type",
            )
        ]


class PriceHistory(models.Model):
    """
    Historical price changes for tracking and analytics.
    """
    price_type = models.ForeignKey(PriceType, on_delete=models.CASCADE, related_name="price_history")
    old_price = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    new_price = models.DecimalField(max_digits=20, decimal_places=4)
    change_percentage = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    changed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.old_price and self.new_price and self.old_price != 0:
            self.change_percentage = ((self.new_price - self.old_price) / self.old_price) * 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.price_type.name}: {self.old_price or 'N/A'} → {self.new_price} ({self.changed_at:%Y-%m-%d %H:%M})"

    class Meta:
        ordering = ["-changed_at"]
        verbose_name_plural = "Price Histories"
