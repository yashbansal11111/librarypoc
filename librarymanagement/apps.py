from django.apps import AppConfig


class LibrarymanagementConfig(AppConfig):
    name = 'librarymanagement'

    def ready(self):
        from librarymanagement import updater
        updater.start()