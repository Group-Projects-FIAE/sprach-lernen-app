from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard-alt'),
]



