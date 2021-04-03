"""MLCICD URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from cicd4ml.views import register_runner, get_job, new_job, new_metric, show_metrics

urlpatterns = [
    path('admin/', admin.site.urls),
    path('view_report', show_metrics),
    path('api/', include([
        path('register_runner', register_runner),
        path('get_job', get_job),
        path('new_job', new_job),
        path('new_metrics', new_metric)
    ]))
]
