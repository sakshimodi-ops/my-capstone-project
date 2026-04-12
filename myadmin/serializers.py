from rest_framework import serializers
from myadmin.models import (
    User,
    Feedback,
    Shelter,
    Product_form,
    Order_table,
    Pet,
    PetHealth
)
from myadmin.models import *


# =======================
# User Serializer
# =======================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


# =======================
# Feedback Serializer
# =======================
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


# =======================
# Shelter Serializer
# =======================
class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = '__all__'


# =======================
# Product Serializer
# =======================
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_form
        fields = '__all__'


# =======================
# Order Serializer
# =======================
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order_table
        fields = '__all__'


# =======================
# Pet Serializer
# =======================
from rest_framework import serializers
from .models import Pet, PetHealth


class PetHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetHealth
        fields = '__all__'


class PetSerializer(serializers.ModelSerializer):
    health_records = PetHealthSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Pet
        fields = '__all__'


# serializers.py
from rest_framework import serializers
from .models import ShelterPayment

class ShelterPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelterPayment
        fields = '__all__'
