from django.urls import path
from . import views

urlpatterns = [
    path('lists/', views.VocabListView.as_view(), name='vocab_lists'),
    path('lists/<int:pk>/', views.ListDetailView.as_view(), name='list_detail'),
    path('lists/create/', views.CreateListView.as_view(), name='create_list'),
    path('lists/<int:pk>/activate/', views.SetActiveListView.as_view(), name='set_active_list'),
    path('lists/<int:pk>/delete/', views.DeleteListView.as_view(), name='delete_list'),
    path('vocabulary/', views.VocabularyView.as_view(), name='vocabulary'),
]