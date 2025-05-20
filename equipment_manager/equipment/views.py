from datetime import date
from django.utils import timezone
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
from rest_framework.views import APIView
# —————————————————————————————————————————
# 4) Локальные модели и сериализаторы
# —————————————————————————————————————————
from .models import Equipment, Place, Status, Log
from .serializers import EquipmentSerializer, PlaceSerializer, StatusSerializer, LogSerializer


from rest_framework import viewsets

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
        'status_id': ['exact'],
    }
    search_fields = [
        'article',
        'inventory_number',
        'name',
    ]

    #узнать можно ли изменить get_queryset, чтобы всё корректно отрабатывало

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




class StatusViewSet(generics.ListCreateAPIView):
    """
    API‑ручка:
      • GET  /place/     — список с фильтрацией и поиском
      • POST /place/     — создание нового объекта
    """
    # Базовый набор полей
    queryset = Status.objects.all()
    serializer_class = StatusSerializer 


    # Фильтрация через django‑filters и DRF SearchFilter
    filter_backends = [
        DjangoFilterBackend,       # точная фильтрация по полям ниже
        filters.SearchFilter       # поиск по тексту
    ]
    filterset_fields = {
        'name_of_status': ['exact', 'icontains']
    }
    search_fields = [
        'name_of_status'
    ]


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    

    



class ReturnEquipmentAPIView(APIView):
    def post(self, request):
        equipment_id = request.data.get('equipment_id')

        if not equipment_id:
            return Response({"error": "equipment_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            equipment = Equipment.objects.get(pk=equipment_id)
        except Equipment.DoesNotExist:
            return Response({"error": "Оборудование не найдено"}, status=status.HTTP_404_NOT_FOUND)

        latest_log = Log.objects.filter(equipment=equipment).order_by('-start_date_of_using').first()

        if not latest_log:
            return Response({"error": "Нет записей в журнале для этого оборудования"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            latest_log.end_date_of_using = timezone.now()  
            if request.data.get('destination'):
                latest_log.destination = request.data.get('destination')
            if request.data.get('application_number'):
                latest_log.application_number = request.data.get('application_number')
            if request.data.get('name_of_receiver'):
                latest_log.name_of_receiver = request.data.get('name_of_receiver')
            latest_log.save()

            equipment.status_id = 1  # Статус "доступно"
            equipment.save()

            return Response({
                "success": True,
                "message": "Оборудование успешно возвращено",
                "log_id": latest_log.id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"Произошла ошибка: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Ловим любые исключения и возвращаем ошибку
            return Response({
                "error": f"Произошла ошибка: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)