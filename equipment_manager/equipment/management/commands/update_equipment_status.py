from django.core.management.base import BaseCommand
from django.utils.timezone import now
from equipment.models import Log, Equipment, Status
from django.db.models import Max, Subquery, OuterRef

class Command(BaseCommand):
    help = 'Обновляет статус оборудования, если срок использования истек и оно не возвращено'

    def handle(self, *args, **kwargs):
        today = now().date()

        try:
            # Получаем статус "неизвестно" (например, id=3) и статус "в использовании" (например, id=2)
            status_unknown = Status.objects.get(id=3)
            status_in_use = Status.objects.get(id=2)
        except Status.DoesNotExist:
            self.stderr.write("Один из нужных статусов (id=2 или id=3) не найден.")
            return

        updated = 0

        # Получаем последние записи Log по каждому оборудованию
        latest_logs = (
            Log.objects
            .values('equipment')  # группируем по оборудованию
            .annotate(latest_start=Max('start_date_of_using'))  # находим самую позднюю дату выдачи
        )

        # Для каждой такой записи проверим, просрочена ли она и надо ли обновлять статус
        for entry in latest_logs:
            equipment_id = entry['equipment']
            latest_date = entry['latest_start']

            # Получаем соответствующую запись Log
            log = Log.objects.filter(
                equipment_id=equipment_id,
                start_date_of_using=latest_date
            ).first()

            if log and log.end_date_of_using and log.end_date_of_using < today:
                equipment = log.equipment
                if equipment.status == status_in_use:
                    # Обновляем статус оборудования
                    equipment.status = status_unknown
                    equipment.save()

                    # Обновляем дату окончания использования
                    log.end_date_of_using = today
                    log.save()

                    updated += 1

        self.stdout.write(f"Обновлено {updated} единиц оборудования.")
