from django.urls import path

from lessons import views

urlpatterns = [
    path('input/<int:pk>/', views.lesson_input, name="lesson_input"),
    path('select/<int:pk>/', views.lesson_select, name="lesson_select"),

]