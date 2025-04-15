from django.contrib import admin
from .models import *

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_of_status')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'inventory_number', 'name', 'location', 'status_id', 'default_location_id', 'equipment_manager', 'commissioning_date')

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipment_id', 'destination', 'start_date_of_using', 'end_date_of_using', 'application_number', 'name_of_receiver')