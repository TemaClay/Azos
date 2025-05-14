from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from equipment.views import (
    EquipmentListView,
    EquipmentListCreateAPIView,
    EquipmentRetrieveUpdateDestroyAPIView,
    PlaceListCreateAPIView,
    StatusViewSet,
    LogViewSet,
    ReturnEquipmentAPIView
)

urlpatterns = [

    # Стандартный вход/выход Django
    path('accounts/', include('django.contrib.auth.urls')),

    # HTML‑страница со списком оборудования
    path('', EquipmentListView.as_view(), name='equipment-list'),

    # JWT‑токены
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # REST API
    # GET  /api/equipment/       — список (+фильтрация/поиск)
    # POST /api/equipment/       — создать новый объект
    path('api/equipment/', EquipmentListCreateAPIView.as_view(), name='equipment-list-create'),

    # REST API
    # GET  /api/place/       — список (+фильтрация/поиск)
    # POST /api/place/       — создать новый объект
    path('api/place/', PlaceListCreateAPIView.as_view(), name='place-list-create'),
    
    # GET    /api/equipment/<pk>/   — детали
    # PATCH  /api/equipment/<pk>/   — частичное обновление
    # DELETE /api/equipment/<pk>/   — «списать» (перевести в status_id=4)
    path('api/equipment/<int:pk>/', EquipmentRetrieveUpdateDestroyAPIView.as_view(), name='equipment-detail'),

    # GET  /api/status/       — список (+фильтрация/поиск)
    # POST /api/status/       — создать новый объект
    path('api/status/', StatusViewSet.as_view(), name='status-list-create'),


    # GET  /api/log/       — список (+фильтрация/поиск)
    # POST /api/log/       — создать новый объект
    path('api/log/', LogViewSet.as_view({'get': 'list', 'post': 'create',}), name='log-list'),


    # GET    /api/log/<pk>/   — детали
    # PATCH  /api/log/<pk>/   — частичное обновление
    path('api/log/<pk>/', LogViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update',}), name="log-detail"),

    # POST /api/equipment/return/ - id возвращаемого оборудования, с возможностью изменить destination, application_number, name_of_receiver в Log
    path('api/equipment/return/', ReturnEquipmentAPIView.as_view(), name='equipment-return'),
]

# Для обслуживания медиа-файлов (если нужно)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
