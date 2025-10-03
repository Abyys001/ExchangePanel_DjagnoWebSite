# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from .models import Price, PriceHistory

# @receiver(pre_save, sender=Price)
# def log_price_change(sender, instance, **kwargs):
#     if instance.pk:  # Existing price (update)
#         try:
#             old_instance = Price.objects.get(pk=instance.pk)
#             if old_instance.price != instance.price:
#                 # Calculate percentage change
#                 change_percentage = ((instance.price - old_instance.price) / old_instance.price) * 100
                
#                 # Create price history record
#                 PriceHistory.objects.create(
#                     price_type=instance.price_type,
#                     old_price=old_instance.price,
#                     new_price=instance.price,
#                     change_percentage=change_percentage,
#                     changed_at=timezone.now(),
#                     notes=f"Price updated from {old_instance.price} to {instance.price}"
#                 )
#         except Price.DoesNotExist:
#             pass
#     else:  # New price (create)
#         # No old price to compare with
#         pass

# @receiver(post_save, sender=Price)
# def set_current_price(sender, instance, created, **kwargs):
#     if created:
#         # Set this as the current price for the price type
#         Price.objects.filter(price_type=instance.price_type).exclude(pk=instance.pk).update(is_current=False)
#         instance.is_current = True
#         instance.save()