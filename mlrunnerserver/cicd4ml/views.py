from django.shortcuts import render
from django.http.response import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from http import HTTPStatus

from cicd4ml.models import Runner, RegisteredRunner, Job, Project, Metric
from cicd4ml.services import GoogleCloudPlatform

import json


@csrf_exempt
@require_POST
def register_runner(request):
    runner_name = request.POST.get('runner_name')
    registration_key = request.POST.get('key')
    ip_address = request.POST.get('ip_address')

    runner = Runner.objects.filter(
        registration_key=registration_key
    ).first()

    if runner:
        registered_runner = RegisteredRunner.objects.create(
            runner=runner,
            name=runner_name,
            ip_address=ip_address,
            state=RegisteredRunner.ALIVE,
            connected_at=datetime.now(),
            last_heart_beat=datetime.now()
        )
        return JsonResponse({
            'error': False,
            'id': registered_runner.id,
            'project': runner.project.name
        }, status=HTTPStatus.OK)

    return JsonResponse({
        'error': True,
        'code': 404,
        'message': 'RUNNER_NOT_FOUND'
    }, status=HTTPStatus.NOT_FOUND)


@require_GET
def get_job(request):
    register_runner_id = request.GET.get('runner_id')
    registered_runner = RegisteredRunner.objects.get(
        id=register_runner_id, state=RegisteredRunner.ALIVE
    )
    job = Job.objects.filter(
        project=registered_runner.runner.project,
        state=Job.QUEUED
    ).first()

    if job:
        job.assigned_runner = registered_runner
        job.assigned_date = datetime.now()
        job.state = job.RUNNING
        job.save()
        return JsonResponse([{
            'id': job.id,
            'error': False,
            'repo': registered_runner.runner.project.repo_url,
            'stage': job.stage
        }], status=HTTPStatus.OK, safe=False)

    return JsonResponse({
        'error': False,
    }, status=HTTPStatus.NO_CONTENT)


@csrf_exempt
@require_POST
def new_job(request):
    project_name = request.POST.get('project_name')
    project = Project.objects.get(name=project_name)
    new_job_object = Job.objects.create(
        project=project,
        stage='NEW PUSH',
        state=Job.QUEUED,
    )
    first_runner = project.runner_set.all()[0]
    google_service = GoogleCloudPlatform()
    google_service.prepareServer('Smoked Meat!', first_runner.registration_key)
    return JsonResponse({
        'error': False,
    }, status=HTTPStatus.NO_CONTENT)


@csrf_exempt
@require_POST
def new_metric(request):
    project_name = request.POST.get('project_name')
    project_object = Project.objects.get(name=project_name)
    metrics = request.POST.get('metrics')
    metric_object = Metric.objects.create(
        project=project_object,
        values=metrics
    )

    return JsonResponse({
        'error': False,
    }, status=HTTPStatus.NO_CONTENT)


@require_GET
def show_metrics(request):
    project_name = request.GET.get('project_name')
    project_object = Project.objects.get(name=project_name)
    metrics = Metric.objects.filter(project=project_object)
    labels = []
    data = []
    for metric in metrics:
        labels.append(metric.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        jsoned_metrics = json.loads(metric.values)
        data.append(jsoned_metrics.get('accuracy'))
    return render(request, 'report.html', {
        'labels': labels,
        'data': data,
    })