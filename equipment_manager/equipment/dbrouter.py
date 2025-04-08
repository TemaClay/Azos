class NoMigrations:
    def allow_migrate(self, db, app_label, **hints):
        return app_label != "equipment"