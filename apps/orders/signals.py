import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.orders.models import Order, OrderItem, Review
from common.models.driver import DriverProfile

logger = logging.getLogger('main')


@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    if created:
        async_to_sync(channel_layer.group_send)(
            f"restaurant_{instance.restaurant_id}",
            {"type": "send_notification", "message": f"New order: {instance.order_number}"}
        )
    async_to_sync(channel_layer.group_send)(
        f"order_{instance.order_number}",
        {"type": "send_notification", "message": f"Order status updated: {instance.status}"}
    )
    if instance.status == 'dl' and instance.driver:
        try:
            dp = DriverProfile.objects.get(user=instance.driver)
            dp.total_deliveries = (dp.total_deliveries or 0) + 1
            dp.save(update_fields=['total_deliveries'])
        except DriverProfile.DoesNotExist:
            pass



@receiver(post_save, sender=Review)
def update_restaurant_rating(sender, instance, created, **kwargs):
    if created and instance.restaurant:
        instance.restaurant.update_average_rating()

@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_totals(sender, instance, **kwargs):
    if not getattr(instance, '_skip_recalc', False):
        instance.order.calculate_total()

