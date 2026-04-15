# Standard Library Imports
import logging
from decimal import Decimal

# Third-Party Imports (Django)
from django.db import transaction
from django.db.models import Avg,Count,Sum,F

# Local Imports
from apps.orders.models import CartItem, Order, OrderItem

logger = logging.getLogger('main')


class CartService:
    @staticmethod
    @transaction.atomic
    def update_cart(user, menu_item, quantity):
        existing = CartItem.objects.filter(user=user, menu_item=menu_item).first()
        if existing:
            existing.quantity += quantity
            existing.save(update_fields=['quantity'])
            return existing
        return CartItem.objects.create(user=user, menu_item=menu_item, quantity=quantity)

    @staticmethod
    def cart_total(user):
        items = CartItem.objects.filter(user=user).select_related('menu_item').aggregate(Sum("quantity"),orvalue=Sum(F("menu_item__price")*F("quantity")))
        total = Decimal('0.00')
        total = items["orvalue"]
        return total.quantize(Decimal('0.01'))

    @staticmethod
    @transaction.atomic
    def checkout(user, special_instructions=''):
        cart_items = CartItem.objects.filter(user=user).select_for_update().select_related('menu_item', 'menu_item__restaurant')
        if not cart_items.exists():
            raise ValueError("cart is empty")

        restaurants = set(ci.menu_item.restaurant_id for ci in cart_items)
        if len(restaurants) > 1:
            raise ValueError("all items must belong to same restaurant")

        restaurant = cart_items.first().menu_item.restaurant

        #MINIMUM ORDER CHECK
        cart_total = sum(ci.menu_item.price * ci.quantity for ci in cart_items)
        if cart_total < restaurant.minimum_order:
            raise ValueError(f"Minimum order amount is {restaurant.minimum_order}")

        try:
            dadr = user.customer_profile.default_adress
        except Exception:
            dadr = None
        if not dadr:
            raise ValueError("default delivery address not found")


        order = Order.objects.create(
            customer=user,
            restaurant=restaurant,
            delivery_address=dadr,
            adratorder=dadr.address,
            special_instructions=special_instructions,
        )
        
        ois = list()

        for ci in cart_items:
            oi = OrderItem(
                order=order,
                menu_item=ci.menu_item,
                quantity=ci.quantity,
                uprice=ci.menu_item.price,
            )
            oi._skip_recalc = True
            ois.append(oi)
        OrderItem.objects.bulk_create(ois)
        order.calculate_total()

        order.calculate_eta()
        cart_items.delete()
        return order
