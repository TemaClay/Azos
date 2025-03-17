from django.urls import path
from .views import EquipmentListCreateAPIView, EquipmentRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('equipment/', EquipmentListCreateAPIView.as_view(), name='equipment-list'),
    path('equipment/<int:pk>/', EquipmentRetrieveUpdateDestroyAPIView.as_view(), name='equipment-detail'),
]