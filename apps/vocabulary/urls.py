from django.urls import path
from .views import WordListView, WordDetailView

urlpatterns = [
    path('words/', WordListView.as_view(), name='word-list'),
    path('words/<uuid:id>/', WordDetailView.as_view(), name='word-detail'),
]