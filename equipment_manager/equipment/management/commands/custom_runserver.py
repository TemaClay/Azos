from django.core.management.commands.runserver import Command as RunserverCommand
from django.conf import settings
import sys

"""custom_runserver - это функционал для реализации аргумента --db: 
возможность запускать сервер с разными базами данных.
Пример: python manage.py custom_runserver --db postgresql_db
"""

class Command(RunserverCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--db', type=str, help="Выберите базу данных (default, postgresql_db, mysql_db)")

    def handle(self, *args, **options):
        db_name = options.get('db')
        if db_name and db_name in settings.DATABASES:
            settings.DATABASES['default'] = settings.DATABASES[db_name]
            print(f"🔥 Используется база данных: {db_name}")  # Для отладки

        super().handle(*args, **options)