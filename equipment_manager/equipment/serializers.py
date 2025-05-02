from rest_framework import serializers
from .models import Equipment, Place  # Импортируйте вашу модель

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment  # Укажите модель
        fields = '__all__' 

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place  # Укажите модель
        fields = '__all__' 