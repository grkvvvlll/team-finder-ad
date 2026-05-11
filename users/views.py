"""Представления приложения users."""

import json
from http import HTTPStatus

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm, EditProfileForm, ChangePasswordForm
from .models import User, Skill
from .utils import paginate_queryset


def register(request):
    """Регистрирует нового пользователя."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Замечание 1: создание пользователя перенесено в форму
            form.save()
            return redirect('users:login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Выполняет вход пользователя в систему."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('projects:list')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Выполняет выход пользователя из системы."""
    logout(request)
    return redirect('projects:list')


def user_detail(request, user_id):
    """Отображает профиль пользователя."""
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user-details.html', {'user': user})


@login_required
def edit_profile(request):
    """Редактирует профиль текущего пользователя."""
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user, current_user=user)
        if form.is_valid():
            form.save()
            return redirect('users:detail', user_id=user.pk)
    else:
        form = EditProfileForm(instance=user, current_user=user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Изменяет пароль текущего пользователя."""
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            login(request, user)
            return redirect('users:detail', user_id=user.pk)
    else:
        form = ChangePasswordForm(user)
    return render(request, 'users/change_password.html', {'form': form})


def users_list(request):
    """Отображает список всех пользователей с фильтрацией по навыкам."""
    skill_name = request.GET.get('skill')
    all_skills = Skill.objects.all()
    users = User.objects.all().order_by('id')
    active_skill = None
    query_prefix = ''

    if skill_name:
        active_skill = skill_name
        users = users.filter(skills__name=skill_name)
        query_prefix = f'skill={skill_name}&'

    # Замечание 2, 3: используем вынесенную функцию пагинации
    page_obj = paginate_queryset(users, request)

    return render(request, 'users/participants.html', {
        'page_obj': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
        'query_prefix': query_prefix,
    })


def skills_autocomplete(request):
    """Возвращает список навыков для автодополнения."""
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q).values('id', 'name')[:10]
    return JsonResponse(list(skills), safe=False)


@login_required
@require_POST
def add_skill(request, user_id):
    """Добавляет навык в профиль пользователя."""
    user = get_object_or_404(User, pk=user_id)
    if request.user != user:
        # Замечание 4: используем HTTPStatus вместо числового кода
        return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)

    try:
        data = json.loads(request.body)
    except Exception:
        data = {}

    skill_id = data.get('skill_id')
    name = data.get('name')
    created = False
    added = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        # Замечание 5: используем HTTPStatus вместо числового кода
        return JsonResponse(
            {'error': 'skill_id or name required'},
            status=HTTPStatus.BAD_REQUEST
        )

    # Замечание 6: используем filter().exists() вместо загрузки всех записей
    if not user.skills.filter(pk=skill.pk).exists():
        user.skills.add(skill)
        added = True

    return JsonResponse({
        'skill_id': skill.pk,
        'id': skill.pk,
        'name': skill.name,
        'created': created,
        'added': added,
    })


@login_required
@require_POST
def remove_skill(request, user_id, skill_id):
    """Удаляет навык из профиля пользователя."""
    user = get_object_or_404(User, pk=user_id)
    if request.user != user:
        # Замечание 7: используем HTTPStatus вместо числового кода
        return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)

    skill = get_object_or_404(Skill, pk=skill_id)

    # Замечание 8: используем filter().exists() вместо загрузки всех записей
    if not user.skills.filter(pk=skill.pk).exists():
        # Замечание 9: используем HTTPStatus вместо числового кода
        return JsonResponse({'error': 'Skill not found'}, status=HTTPStatus.BAD_REQUEST)

    user.skills.remove(skill)
    return JsonResponse({'status': 'ok'})
