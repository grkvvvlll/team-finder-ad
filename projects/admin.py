"""Настройки админки для приложения projects."""

from django.contrib import admin
from .models import Project

admin.site.register(Project)
