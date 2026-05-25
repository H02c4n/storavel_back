from django.urls import path
from .views import StoryQuizzesView, QuizAttemptView, QuizHistoryView

urlpatterns = [
    path('stories/<slug:slug>/', StoryQuizzesView.as_view(), name='story-quizzes'),
    path('stories/<slug:slug>/attempt/', QuizAttemptView.as_view(), name='quiz-attempt'),
    path('history/', QuizHistoryView.as_view(), name='quiz-history'),
]