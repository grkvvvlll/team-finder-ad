"""Формы приложения users."""

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import User
from .utils import (
    NAME_MAX_LENGTH,
    clean_github_url,
    clean_phone,
)


class RegisterForm(forms.Form):
    """Форма регистрации нового пользователя."""

    name = forms.CharField(max_length=NAME_MAX_LENGTH, label='Имя')
    surname = forms.CharField(max_length=NAME_MAX_LENGTH, label='Фамилия')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    def clean_email(self):
        """Проверяет уникальность email."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self):
        """Создаёт и возвращает нового пользователя."""
        return User.objects.create_user(
            email=self.cleaned_data['email'],
            name=self.cleaned_data['name'],
            surname=self.cleaned_data['surname'],
            password=self.cleaned_data['password'],
        )


class LoginForm(forms.Form):
    """Форма входа в систему."""

    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    def clean(self):
        """Проверяет правильность введённых данных."""
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            self.user = authenticate(username=email, password=password)
            if self.user is None:
                raise ValidationError('Неверный email или пароль')
        return cleaned

    def get_user(self):
        """Возвращает аутентифицированного пользователя."""
        return getattr(self, 'user', None)


class EditProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя."""

    phone = forms.CharField(required=False, label='Номер телефона')
    github_url = forms.URLField(required=False, label='Ссылка на профиль GitHub')

    class Meta:
        """Мета-настройки формы EditProfileForm."""

        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'avatar': forms.FileInput(),
            'about': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'about': 'Обо мне',
        }

    def __init__(self, *args, **kwargs):
        """Инициализирует форму с текущим пользователем."""
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

    def clean_phone(self):
        """Валидирует и нормализует номер телефона."""
        return clean_phone(self.cleaned_data.get('phone'), self.current_user)

    def clean_github_url(self):
        """Валидирует ссылку на GitHub."""
        return clean_github_url(self.cleaned_data.get('github_url', ''))


class ChangePasswordForm(forms.Form):
    """Форма смены пароля."""

    old_password = forms.CharField(widget=forms.PasswordInput, label='Старый пароль')
    new_password1 = forms.CharField(widget=forms.PasswordInput, label='Новый пароль')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='Повторите новый пароль')

    def __init__(self, user, *args, **kwargs):
        """Инициализирует форму с экземпляром пользователя."""
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """Проверяет правильность старого пароля."""
        old_pw = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_pw):
            raise ValidationError('Неверный текущий пароль')
        return old_pw

    def clean(self):
        """Проверяет совпадение новых паролей."""
        cleaned = super().clean()
        pw1 = cleaned.get('new_password1')
        pw2 = cleaned.get('new_password2')
        if pw1 and pw2 and pw1 != pw2:
            raise ValidationError('Пароли не совпадают')
        return cleaned

    def save(self):
        """Сохраняет новый пароль."""
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
