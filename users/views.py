"""Представления приложения users."""

import json

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm, EditProfileForm, ChangePasswordForm
from .models import User, Skill


def register(request):
    """Регистрирует нового пользователя."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                email=form.cleaned_data['email'],
                name=form.cleaned_data['name'],
                surname=form.cleaned_data['surname'],
                password=form.cleaned_data['password'],
            )
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

    paginator = Paginator(users, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

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
        return JsonResponse({'error': 'Forbidden'}, status=403)

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
        return JsonResponse({'error': 'skill_id or name required'}, status=400)

    if skill not in user.skills.all():
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
        return JsonResponse({'error': 'Forbidden'}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    if skill not in user.skills.all():
        return JsonResponse({'error': 'Skill not found'}, status=400)

    user.skills.remove(skill)
    return JsonResponse({'status': 'ok'})
