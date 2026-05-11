"""Представления приложения projects."""

from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project, STATUS_OPEN, STATUS_CLOSED
from .utils import paginate_queryset


def project_list(request):
    """Отображает список всех проектов."""
    projects = Project.objects.select_related('owner').order_by('-created_at')
    page_obj = paginate_queryset(projects, request)
    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'projects': projects,
    })


def project_detail(request, project_id):
    """Отображает страницу отдельного проекта."""
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'),
        pk=project_id
    )
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project(request):
    """Создаёт новый проект."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect('projects:detail', project_id=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def edit_project(request, project_id):
    """Редактирует существующий проект."""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:detail', project_id=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
@require_POST
def complete_project(request, project_id):
    """Завершает проект, меняя его статус на закрытый."""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if project.status != STATUS_OPEN:
        return JsonResponse(
            {'error': 'Already closed'},
            status=HTTPStatus.BAD_REQUEST
        )
    project.status = STATUS_CLOSED
    project.save()
    return JsonResponse({'status': 'ok', 'project_status': STATUS_CLOSED})


@login_required
@require_POST
def toggle_participate(request, project_id):
    """Добавляет или убирает пользователя из участников проекта."""
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    is_participant = project.participants.filter(pk=user.pk).exists()
    if is_participant:
        project.participants.remove(user)
        participant = False
    else:
        project.participants.add(user)
        participant = True
    return JsonResponse({'status': 'ok', 'participant': participant})
