
from rest_framework import serializers
from .models import Product, Cart, Contact

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity', 'user']

class ContactSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Contact
        fields = ['id', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone']

    def create(self, validated_data):
        user = self.context['request'].user
        contact = Contact.objects.create(user=user, **validated_data)
        return contact