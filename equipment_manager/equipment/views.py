# —————————————————————————————————————————
# 1) Django HTML‑генерики
# —————————————————————————————————————————
from django.shortcuts import render
from django.views.generic import ListView

# —————————————————————————————————————————
# 2) Django‑filters для DRF
# —————————————————————————————————————————
from django_filters.rest_framework import DjangoFilterBackend

# —————————————————————————————————————————
# 3) DRF core и миксины
# —————————————————————————————————————————
from rest_framework import filters, generics, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# —————————————————————————————————————————
# 4) Локальные модели и сериализаторы
# —————————————————————————————————————————
from .models import Equipment, Place
from .serializers import EquipmentSerializer, PlaceSerializer


class EquipmentListView(ListView):
    """
    HTML‑страница: отображает весь список оборудования.
    Используется в шаблоне 'equipment_list.html'.
    """
    model = Equipment
    template_name = 'equipment_list.html'
    context_object_name = 'equipments'


class EquipmentListCreateAPIView(generics.ListCreateAPIView):
    """
    API‑ручка:
      • GET  /equipment/     — список с фильтрацией и поиском
      • POST /equipment/     — создание нового объекта
    """
    # Базовый набор полей
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


    # Фильтрация через django‑filters и DRF SearchFilter
    filter_backends = [
        DjangoFilterBackend,       # точная фильтрация по полям ниже
        filters.SearchFilter       # поиск по тексту
    ]
    filterset_fields = {
        'equipment_manager': ['exact', 'icontains'],
        'commissioning_date': ['exact'],
        'default_location': ['exact'],
    }
    search_fields = [
        'article',
        'inventory_number',
        'name',
    ]

    def get_queryset(self):
        """
        Добавляем доп. условие:
        если в query string нет show_salvaged=true,
        то отбрасываем объекты со status_id=4.
        """
        qs = super().get_queryset()
        show_salvaged = self.request.query_params.get('show_salvaged', '').lower()

        if show_salvaged != 'true':
            qs = qs.exclude(status_id=4)
        return qs

class PlaceListCreateAPIView(generics.ListCreateAPIView):
    """
    API‑ручка:
      • GET  /place/     — список с фильтрацией и поиском
      • POST /place/     — создание нового объекта
    """
    # Базовый набор полей
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


    # Фильтрация через django‑filters и DRF SearchFilter
    filter_backends = [
        DjangoFilterBackend,       # точная фильтрация по полям ниже
        filters.SearchFilter       # поиск по тексту
    ]
    filterset_fields = {
        'name': ['exact', 'icontains']
    }
    search_fields = [
        'name'
    ]
    

class EquipmentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API‑ручка по path /equipment/<pk>/:
      • GET    — получить детали
      • PATCH  — частичное обновление
      • DELETE — пометить статус как списанное (status_id=4)
    """
    # Какие объекты и как сериализовать
    queryset         = Equipment.objects.all()
    serializer_class = EquipmentSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Вместо физического удаления помечаем статус как "списано" (status_id=4).
        """
        instance = self.get_object()
        instance.status_id = 4
        instance.save()

        # Сериализуем обновлённый объект и возвращаем клиенту
        serializer = self.get_serializer(instance)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )