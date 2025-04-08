from django.contrib import admin
from django.urls import path, include
from equipment import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.EquipmentListView.as_view(), name='equipment-list'),
]