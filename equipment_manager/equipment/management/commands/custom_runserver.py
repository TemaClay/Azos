# equipment/management/commands/custom_runserver.py
from django.core.management.commands.runserver import Command as RunserverCommand
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler

class Command(RunserverCommand):
    help = "Custom runserver with database selection and static files support"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--db', 
            choices=['default', 'postgresql_db', 'mysql_db'],
            default='default',
            help='Select database: default, postgresql_db or mysql_db'
        )

    def handle(self, *args, **options):
        # Установка выбранной БД
        db_name = options['db']
        settings.DATABASES['default'] = settings.DATABASES[db_name]
        print(f"\n🔥🔥🔥 Используем db: {db_name} ({settings.DATABASES[db_name]['ENGINE']})")

        # Включение статических файлов
        if settings.DEBUG:
            options['use_static_handler'] = True
            options['insecure_serving'] = True

        # Переопределение обработчика
        self.get_handler = self._force_static_handler
        super().handle(*args, **options)

    def _force_static_handler(self, *args, **kwargs):
        handler = super().get_handler(*args, **kwargs)
        return StaticFilesHandler(handler) if settings.DEBUG else handler