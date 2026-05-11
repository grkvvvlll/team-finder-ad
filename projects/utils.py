"""Вспомогательные функции приложения projects."""

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator


def validate_github_url(value):
    """Проверяет что ссылка ведёт на GitHub."""
    if value and 'github.com' not in value:
        raise ValidationError('Ссылка должна вести на GitHub')
    return value


def paginate_queryset(queryset, request, per_page=12):
    """Применяет пагинацию к queryset и возвращает текущую страницу."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
