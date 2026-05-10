"""Модели приложения users."""

import io
import random

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


AVATAR_COLORS = [
    '#4A90D9', '#7B68EE', '#20B2AA', '#3CB371',
    '#CD853F', '#708090', '#E07B54', '#5C6BC0',
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


class UserManager(BaseUserManager):
    """Менеджер для модели пользователя."""

    def create_user(self, email, name, surname, password=None, **extra_fields):
        """Создаёт и возвращает обычного пользователя."""
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        avatar_content = generate_avatar(name[0] if name else 'U')
        user.avatar.save(f'avatar_{email}.png', avatar_content, save=False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        """Создаёт и возвращает суперпользователя."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class Skill(models.Model):
    """Модель навыка или технологии."""

    name = models.CharField(max_length=124, unique=True)

    class Meta:
        """Мета-настройки модели Skill."""

        ordering = ['name']

    def __str__(self):
        """Возвращает строковое представление."""
        return self.name

    def __eq__(self, other):
        """Сравнивает навык со строкой или другим навыком."""
        if isinstance(other, str):
            return self.name == other
        return super().__eq__(other)

    def __hash__(self):
        """Возвращает хэш объекта."""
        return super().__hash__()


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с email в качестве логина."""

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/')
    phone = models.CharField(max_length=12, blank=True, null=True, unique=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(blank=True, max_length=256)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, blank=True, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    class Meta:
        """Мета-настройки модели User."""

        ordering = ['id']

    def __str__(self):
        """Возвращает строковое представление."""
        return f'{self.surname} {self.name}'
