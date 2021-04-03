from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    repo_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Runner(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    registration_key = models.CharField(max_length=200)


class RegisteredRunner(models.Model):
    ALIVE = 'ALIVE'
    DEAD = 'DEAD'
    STATE_CHOICES = [
        (ALIVE, 'Alive'),
        (DEAD, 'Dead')
    ]

    runner = models.ForeignKey(Runner, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    connected_at = models.DateTimeField()
    last_heart_beat = models.DateTimeField()

    def __str__(self):
        return self.name


class Job(models.Model):
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    DONE = 'DONE'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'
    STATE_CHOICES = [
        (QUEUED, 'Queued'),
        (RUNNING, 'Running'),
        (DONE, 'Done'),
        (FAILED, 'Failed'),
        (CANCELED, 'Canceled')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    stage = models.CharField(max_length=200)
    assigned_runner = models.ForeignKey(RegisteredRunner, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_date = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Metric(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    values = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
