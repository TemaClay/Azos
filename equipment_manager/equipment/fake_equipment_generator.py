"""
Скрипт для генерации случайных элементов таблицы Equipment внутри вашей БД.

Шаги
1. python manage.py shell
2. exec(open(r"ПУТЬ К \fake_equipment_generator.py", encoding="utf-8").read())

Путь может меняться в зависимости от вас
"""

import random
from datetime import datetime, timedelta
from equipment.models import Equipment, Place, Status
from faker import Faker

fake = Faker()

# Получаем список всех мест и статусов
locations = list(Place.objects.all())
statuses = list(Status.objects.all())

# Список возможных менеджеров
managers = [
    "Иван Иванов",
    "Сергей Сергеев",
    "Петр Петров",
    "Анна Анна",
    "Мария Мариева",
    "Дмитрий Дмитриев"
]

# Параметр если надо удалить все старые элементы внутри Equipment
Equipment.objects.all().delete()

# Генерим 50 записей
for i in range(50):
    Equipment.objects.create(
        article=f"ART-{random.randint(1000, 9999)}",
        inventory_number=f"INV-{random.randint(100000, 999999)}",
        name=fake.word().capitalize() + " " + fake.word(),
        default_location=random.choice(locations),
        status=random.choice(statuses),
        equipment_manager=random.choice(managers),
        commissioning_date=random.randint(1900, 2025),
        location=fake.word()
    )
