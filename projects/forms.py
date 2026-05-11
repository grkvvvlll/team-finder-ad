"""Формы приложения projects."""

from django import forms

from .models import Project, STATUS_CHOICES
from .utils import validate_github_url


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта."""

    github_url = forms.URLField(required=False, label='Ссылка на GitHub')

    class Meta:
        """Мета-настройки формы ProjectForm."""

        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'status': forms.Select(choices=STATUS_CHOICES),
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
