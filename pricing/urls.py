from django.urls import path
from . import views

app_name = "pricing"

urlpatterns = [
    # Category CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),

    # Price views
    path('prices/', views.price_list, name='price_list'),
    path('categories/<slug:category_slug>/prices/', views.category_prices_form, name='category_prices_form'),
    # path('categories/<slug:category_slug>/prices/<int:price_id>/edit/', views.price_form, name='edit_price'),
]
