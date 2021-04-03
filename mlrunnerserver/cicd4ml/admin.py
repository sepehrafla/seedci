from django.contrib import admin
from .models import Project, Runner, RegisteredRunner, Job, Metric

# Register your models here.
admin.site.register(Project)
admin.site.register(Runner)
admin.site.register(RegisteredRunner)
admin.site.register(Job)
admin.site.register(Metric)