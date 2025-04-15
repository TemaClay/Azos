from django.db import models

class Place(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'Places'  # Явное указание имени таблицы

class Status(models.Model):
    name_of_status = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'Status'

class Equipment(models.Model):
    article = models.CharField(max_length=255, verbose_name='Артикул')
    inventory_number = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name='Инвентарный номер'
    )
    name = models.CharField(max_length=255, verbose_name='Название')
    default_location = models.ForeignKey(
        Place, 
        default= 1,
        on_delete=models.CASCADE, 
        db_column='default_location_id',
        verbose_name='Локация'
    )
    status = models.ForeignKey(
        Status, 
        on_delete=models.CASCADE, 
        db_column='Status_id',
        verbose_name='Статус'
    )
    commissioning_date = models.CharField(  # Исправленная опечатка
        max_length=255,
        default = 'Не указано',
        verbose_name='Дата ввода в эксплуатацию'
    )
    equipment_manager = models.CharField(
        max_length=255,
        default='Не указано',  # Значение по умолчанию
        verbose_name='Ответственный'
    )
    location = models.CharField(
        max_length=255,
        default = 'Не указано',
        verbose_name = 'Текущая локация'
    )

    
    class Meta:
        db_table = 'Equipment'

class Log(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, db_column='Equipment_id')
    destination = models.CharField(max_length=255, blank=True)
    start_date_of_using = models.DateField()
    application_number = models.CharField(max_length=255, blank=True)
    end_date_of_using = models.DateField(null=True, blank=True)
    name_of_receiver = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'Log'