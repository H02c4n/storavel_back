from django.urls import path
from .views import (UserWordListView, UserWordDetailView, UserWordReviewView, DueReviewsView,
                    ExportNotebookView, UserWordCollectionListView, UserWordCollectionDetailView,
                    AddWordToCollectionView, RemoveWordFromCollectionView)

urlpatterns = [
    path('words/', UserWordListView.as_view(), name='notebook-words'),
    path('words/<uuid:id>/', UserWordDetailView.as_view(), name='notebook-word-detail'),
    path('words/<uuid:id>/review/', UserWordReviewView.as_view(), name='notebook-word-review'),
    path('words/due-review/', DueReviewsView.as_view(), name='due-reviews'),
    path('export/', ExportNotebookView.as_view(), name='notebook-export'),
    path('collections/', UserWordCollectionListView.as_view(), name='collections'),
    path('collections/<uuid:id>/', UserWordCollectionDetailView.as_view(), name='collection-detail'),
    path('collections/<uuid:id>/words/add/', AddWordToCollectionView.as_view(), name='add-word'),
    path('collections/<uuid:id>/words/remove/', RemoveWordFromCollectionView.as_view(), name='remove-word'),
]