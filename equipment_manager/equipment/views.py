from django.views.generic import ListView
from .models import Equipment
from .serializers import EquipmentSerializer
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend


class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment_list.html'
    context_object_name = 'equipments'

from django.shortcuts import render
from rest_framework import generics

from rest_framework import status
import json
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import chardet

class EquipmentCreate(generics.ListCreateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


class ExampleView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)

@api_view(['POST'])
def handle_equipment(request):
    permission_classes = [IsAuthenticated]
    try:
        if isinstance(request.data, dict):
            data = request.data
        else:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except UnicodeDecodeError:
                data = json.loads(request.body.decode('cp1251'))
        
        action = data.get('action')
        equipment_data = data.get('equipment')

        if not action or not equipment_data:
            return Response(
                {"error": "Некорректный запрос: отсутствует action или equipment"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if action == "insert":
            return add_equipment(equipment_data)
        elif action == "update":
            return update_equipment(equipment_data)
        elif action == "delete":
            return delete_equipment(equipment_data)
        else:
            return Response(
                {"error": "Неизвестное действие"},
                status=status.HTTP_400_BAD_REQUEST
            )

    except json.JSONDecodeError:
        return Response(
            {"error": "Неверный формат JSON"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def add_equipment(data):
    serializer = EquipmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Оборудование добавлено", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

def update_equipment(data):
    try:
        equipment = Equipment.objects.get(inventory_number=data['inventory_number'])
        serializer = EquipmentSerializer(equipment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Оборудование обновлено", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    except Equipment.DoesNotExist:
        return Response(
            {"error": "Оборудование не найдено"},
            status=status.HTTP_404_NOT_FOUND
        )

def delete_equipment(data):
    try:
        equipment = Equipment.objects.get(inventory_number=data['inventory_number'])
        equipment.delete()
        return Response(
            {"message": "Оборудование удалено"},
            status=status.HTTP_200_OK
        )
    except Equipment.DoesNotExist:
        return Response(
            {"error": "Оборудование не найдено"},
            status=status.HTTP_404_NOT_FOUND
        )

class EquipmentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]  
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

    # Подключаем оба фильтрующих бэкенда:
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    # Фильтрация по точному совпадению:
    filterset_fields = ['equipment_manager', 'commissioning_date', 'default_location'] 
    # Общий поиск по текстовым полям (по параметру ?search=...):
    search_fields = ['article', 'inventory_number', 'name']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Получаем параметр show_salvaged из строки запроса (по умолчанию пустая строка)
        show_salvaged = self.request.query_params.get('show_salvaged', '').lower()
        # иначе
        if show_salvaged != 'true':
            queryset = queryset.exclude(status_id=4)


        return queryset