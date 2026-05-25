from django.urls import path
from .views import ProgressView, StreakView, ActivityView, AchievementsView

urlpatterns = [
    path('', ProgressView.as_view(), name='progress'),
    path('streak/', StreakView.as_view(), name='streak'),
    path('activity/', ActivityView.as_view(), name='activity'),
    path('achievements/', AchievementsView.as_view(), name='achievements'),
]