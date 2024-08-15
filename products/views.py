from django.shortcuts import render
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import ContactSerializer, CartSerializer
from .models import Cart, Product, Contact
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Autorization
class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


# registration
class RegisterAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email уже используется'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
        return Response({'message': 'Пользователь был успешно создан'}, status=status.HTTP_201_CREATED)


#product_list

class ProductListAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartAPIView(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        user = request.user

        product = Product.objects.get(id=product_id)
        cart, created = Cart.objects.get_or_create(user=user, product=product)
        cart.quantity = quantity
        cart.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user = request.user
        try:
            cart = Cart.objects.get(user=user, pk=pk)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({'error': 'Товар не найден в корзине'}, status=status.HTTP_404_NOT_FOUND)


class ContactAPIView(APIView):
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            contact = Contact.objects.get(pk=pk)
            contact.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contact.DoesNotExist:
            return Response({'error': 'Контакт не найден'}, status=status.HTTP_404_NOT_FOUND)

#Добавил функционал офрмления заказа 
class OrderAPIView(APIView):
    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items:
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=user)

        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

        cart_items.delete()  # Очистить корзину после создания заказа

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
