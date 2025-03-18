class DefaultRouter:
    """
    Роутер для SQLite (по умолчанию).
    """
    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'


class PostgreSQLRouter:
    """
    Роутер для PostgreSQL.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'your_postgres_app':
            return 'postgresql_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'your_postgres_app':
            return 'postgresql_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == 'your_postgres_app' or
            obj2._meta.app_label == 'your_postgres_app'
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'your_postgres_app':
            return db == 'postgresql_db'
        return None


class MySQLRouter:
    """
    Роутер для MySQL.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'your_mysql_app':
            return 'mysql_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'your_mysql_app':
            return 'mysql_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == 'your_mysql_app' or
            obj2._meta.app_label == 'your_mysql_app'
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'your_mysql_app':
            return db == 'mysql_db'
        return None