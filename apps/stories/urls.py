from django.urls import path
from .views import (StoryListView, StoryDetailView, StoryVersionListView, StoryVersionDetailView,
                    StoryWordsView, UserStoryProgressView, UserNoteView)

urlpatterns = [
    path('', StoryListView.as_view(), name='story-list'),
    path('<slug:slug>/', StoryDetailView.as_view(), name='story-detail'),
    path('<slug:slug>/versions/', StoryVersionListView.as_view(), name='story-versions'),
    path('<slug:slug>/versions/<str:version_type>/', StoryVersionDetailView.as_view(), name='story-version-detail'),
    path('<slug:slug>/words/', StoryWordsView.as_view(), name='story-words'),
    path('<slug:slug>/progress/', UserStoryProgressView.as_view(), name='story-progress'),
    path('<slug:slug>/note/', UserNoteView.as_view(), name='story-note'),
]