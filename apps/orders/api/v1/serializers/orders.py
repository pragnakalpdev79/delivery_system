from rest_framework import serializers
from apps.orders.models import CartItem, Order, OrderItem, Review
from apps.restaurants.models import MenuItem


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'menu_item', 'quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'uprice', 'special_instructions']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='item_for', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_number', 'customer', 'status', 'delivery_address',
                  'subtotal', 'delivery_fee', 'tax', 'total_amount', 'special_instructions',
                  'estimated_delivery_time', 'actual_delivery_time', 'items', 'created_at']
        read_only_fields = ['customer', 'subtotal', 'delivery_fee', 'tax', 'total_amount',
                            'estimated_delivery_time', 'actual_delivery_time', 'created_at', 'restaurant', 'driver']


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.SC)

    def validate(self, attrs):
        order = self.context['order']
        next_status = attrs['status']
        allowed = order.TRANSITIONS.get(order.status, [])
        if next_status not in allowed:
            raise serializers.ValidationError(f"Invalid transition {order.status} -> {next_status}")
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'customer', 'restaurant', 'menu_item', 'order', 'rating', 'comment', 'created_at']
        read_only_fields = ['customer', 'created_at']

    def validate(self, attrs):
        request = self.context['request']
        order = attrs.get('order')
        if order.customer_id != request.user.id:
            raise serializers.ValidationError("You can review only your own order")
        if order.status != Order.STATE_DL:
            raise serializers.ValidationError("Only delivered orders can be reviewed")
        
        if Review.objects.filter(customer=request.user,order=order).exists():
            raise serializers.ValidationError("You have already reviewed this order")
        return attrs
