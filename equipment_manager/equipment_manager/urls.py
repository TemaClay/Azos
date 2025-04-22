from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('equipment.urls')), #Если пользователь переходит по http://localhost:8000/api/..., Django передаст эту часть URL в маршруты, определённые в приложении equipment.
]

"""
 Функция include() в urlpatterns говорит Django, что если URL начинается 
 с определённого префикса (например, api/), 
 то дальше все оставшиеся части URL должны быть обработаны другим списком маршрутов 
 (в нашем случае — маршруты приложения equipment).
"""