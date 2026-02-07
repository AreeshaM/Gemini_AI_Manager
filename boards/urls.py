from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('update-task/<int:task_id>/', views.update_task_status, name='update_task'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
]
