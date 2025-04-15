from rest_framework import serializers
from .models import Equipment  # Импортируйте вашу модель

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment  # Укажите модель
        fields = '__all__' 