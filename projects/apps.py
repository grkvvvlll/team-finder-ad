"""Конфигурация приложения projects."""

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Класс конфигурации приложения."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
