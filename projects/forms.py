"""Формы приложения projects."""

from django import forms
from django.core.exceptions import ValidationError

from .models import Project


def validate_github_url(value):
    """Проверяет что ссылка ведёт на GitHub."""
    if value and 'github.com' not in value:
        raise ValidationError('Ссылка должна вести на GitHub')
    return value


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта."""

    github_url = forms.URLField(required=False, label='Ссылка на GitHub')

    class Meta:
        """Мета-настройки формы ProjectForm."""

        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'status': forms.Select(choices=Project.STATUS_CHOICES),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'status': 'Статус',
        }

    def clean_github_url(self):
        """Валидирует ссылку на GitHub."""
        url = self.cleaned_data.get('github_url', '')
        validate_github_url(url)
        return url
