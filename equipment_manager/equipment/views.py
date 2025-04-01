from django.views.generic import ListView
from .models import Equipment

class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment_list.html'
    context_object_name = 'equipments'