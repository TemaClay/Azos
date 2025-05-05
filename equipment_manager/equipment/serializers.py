from rest_framework import serializers
from .models import Equipment, Place, Status

class PlaceSerializer(serializers.ModelSerializer):
    """
    Сериализатор вложенного объекта Place.
    Отдаёт id и name, для расширения можно добавить другие поля.
    """
    class Meta:
        model = Place
        fields = ('id', 'name')


class StatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор вложенного объекта Status.
    Отдаёт id и Name_of_status, для расширения можно добавить другие поля.
    """
    class Meta:
        model = Status
        # поле в модели Status называется, например, Name_of_status
        fields = ['id', 'name_of_status']


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Equipment с паттерном:
      - write-only поля: default_location_id, status_id
      - read-only вложенные поля: default_location, status
    """

    # ---- Запись связи с Place по PK ----
    default_location_id = serializers.PrimaryKeyRelatedField(
        source='default_location',       # связывает с полем модели .default_location
        queryset=Place.objects.all(),    # валидирует, что такой Place существует
        write_only=True,                 # не появляется в выходном JSON
        help_text='ID места (Place) для связи'
    )
    # ---- Чтение вложенного объекта Place ----
    default_location = PlaceSerializer(
        read_only=True,                  # нельзя менять через это поле
        help_text='Вложенный объект Place с полями id и name'
    )

    # ---- Запись связи со Status по PK ----
    status_id = serializers.PrimaryKeyRelatedField(
        source='status',                 # связывает с полем модели .status
        queryset=Status.objects.all(),   # валидирует, что такой Status существует
        write_only=True,                 # не появляется в выходном JSON
        help_text='ID статуса (Status) для связи'
    )
    # ---- Чтение вложенного объекта Status ----
    status = StatusSerializer(
        read_only=True,                  # нельзя менять через это поле
        help_text='Вложенный объект Status с полями id и Name_of_status'
    )

    class Meta:
        model = Equipment
        fields = [
            'id',
            'article',
            'inventory_number',
            'name',
            'commissioning_date',
            'equipment_manager',
            'location',
            # поля для записи/чтения связей
            'default_location_id',   # write-only для фронтенда: указать ID места при POST/PATCH
            'default_location',      # read-only для фронтенда: получить объект Place в ответе
            'status_id',             # write-only для фронтенда: указать ID статуса при POST/PATCH
            'status',                # read-only для фронтенда: получить объект Status в ответе
        ]