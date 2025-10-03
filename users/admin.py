from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("username", "role", "is_staff", "is_active",)
    list_filter = ("role", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("username", "password", "role")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "role", "password1", "password2", "is_staff", "is_active")}
        ),
    )
    search_fields = ("username",)
    ordering = ("username",)

admin.site.register(CustomUser, CustomUserAdmin)
