from django.contrib import admin
from django.urls import path, include
from equipment import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.EquipmentListView.as_view(), name='equipment-list'),
    path('equipment/', views.handle_equipment, name='equipment-handle'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]