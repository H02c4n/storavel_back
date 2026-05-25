from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import UserProgress, DailyActivity, UserAchievement, Achievement
from .serializers import UserProgressSerializer, DailyActivitySerializer, UserAchievementSerializer

class ProgressView(generics.RetrieveAPIView):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = UserProgress.objects.get_or_create(user=self.request.user)
        return obj

class StreakView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        progress, _ = UserProgress.objects.get_or_create(user=request.user)
        return Response({
            'current_streak': progress.current_streak_days,
            'longest_streak': progress.longest_streak_days,
            'last_active': progress.last_active_date
        })

class ActivityView(generics.ListAPIView):
    serializer_class = DailyActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        days = self.request.query_params.get('days', 30)
        cutoff = timezone.now().date() - timedelta(days=int(days))
        return DailyActivity.objects.filter(user=self.request.user, date__gte=cutoff).order_by('date')

class AchievementsView(generics.ListAPIView):
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user).select_related('achievement')