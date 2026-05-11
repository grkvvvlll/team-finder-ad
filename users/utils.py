"""Вспомогательные функции приложения users."""

import io
import re
import random

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.paginator import Paginator

from PIL import Image, ImageDraw, ImageFont

NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256

COLOR_CORNFLOWER_BLUE = '#4A90D9'
COLOR_MEDIUM_SLATE_BLUE = '#7B68EE'
COLOR_LIGHT_SEA_GREEN = '#20B2AA'
COLOR_MEDIUM_SEA_GREEN = '#3CB371'
COLOR_PERU = '#CD853F'
COLOR_SLATE_GRAY = '#708090'
COLOR_BURNT_SIENNA = '#E07B54'
COLOR_SLATE_BLUE = '#5C6BC0'

AVATAR_COLORS = [
    COLOR_CORNFLOWER_BLUE,
    COLOR_MEDIUM_SLATE_BLUE,
    COLOR_LIGHT_SEA_GREEN,
    COLOR_MEDIUM_SEA_GREEN,
    COLOR_PERU,
    COLOR_SLATE_GRAY,
    COLOR_BURNT_SIENNA,
    COLOR_SLATE_BLUE,
]


def generate_avatar(letter):
    """Генерирует аватар с буквой на цветном фоне."""
    size = 200
    bg_color = random.choice(AVATAR_COLORS)
    img = Image.new('RGB', (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)
    letter = letter.upper()

    font = None
    for font_path in [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/Library/Fonts/Arial.ttf',
        'C:/Windows/Fonts/arial.ttf',
    ]:
        try:
            font = ImageFont.truetype(font_path, 100)
            break
        except (IOError, OSError):
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (size - (bbox[2] - bbox[0])) / 2 - bbox[0]
    y = (size - (bbox[3] - bbox[1])) / 2 - bbox[1]
    draw.text((x, y), letter, fill='white', font=font)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return ContentFile(buf.read())


def validate_phone(value):
    """Проверяет формат номера телефона."""
    if not value:
        return value
    pattern = r'^(8\d{10}|\+7\d{10})$'
    if not re.match(pattern, value):
        raise ValidationError('Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX')
    return value


def normalize_phone(value):
    """Приводит номер телефона к формату +7."""
    if value and value.startswith('8'):
        return '+7' + value[1:]
    return value


def validate_github_url(value):
    """Проверяет что ссылка ведёт на GitHub."""
    if value and 'github.com' not in value:
        raise ValidationError('Ссылка должна вести на GitHub')
    return value


def clean_phone(phone, current_user=None):
    """Валидирует, нормализует номер телефона и проверяет уникальность."""
    from .models import User  # импорт внутри функции чтобы избежать циклического импорта
    if not phone:
        return None
    validate_phone(phone)
    phone = normalize_phone(phone)
    qs = User.objects.filter(phone=phone)
    if current_user:
        qs = qs.exclude(pk=current_user.pk)
    if qs.exists():
        raise ValidationError('Этот номер телефона уже используется')
    return phone


def clean_github_url(url):
    """Валидирует ссылку на GitHub."""
    validate_github_url(url)
    return url


def paginate_queryset(queryset, request, per_page=12):
    """Применяет пагинацию к queryset и возвращает текущую страницу."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
