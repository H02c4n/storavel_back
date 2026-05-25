from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.stories.models import UserStoryProgress
from apps.quizzes.models import UserQuizAttempt
from .models import UserProgress, DailyActivity


def get_progress(user):
    obj, _ = UserProgress.objects.get_or_create(user=user)
    return obj


def get_activity(user):
    today = timezone.now().date()
    obj, _ = DailyActivity.objects.get_or_create(user=user, date=today)
    return obj


def update_streak(progress):
    today = timezone.now().date()
    last = progress.last_active_date
    if last == today:
        return  # already updated today
    if last and (today - last).days == 1:
        progress.current_streak_days += 1
    elif last and (today - last).days > 1:
        progress.current_streak_days = 1
    else:
        progress.current_streak_days = max(progress.current_streak_days, 1)
    if progress.current_streak_days > progress.longest_streak_days:
        progress.longest_streak_days = progress.current_streak_days
    progress.last_active_date = today


@receiver(post_save, sender=UserStoryProgress)
def on_story_progress_save(sender, instance, **kwargs):
    user = instance.user
    progress = get_progress(user)
    activity = get_activity(user)

    # Recalculate total stories read
    progress.total_stories_read = UserStoryProgress.objects.filter(
        user=user, completed=True
    ).count()

    # XP for reading: 1 XP per minute estimated (capped at story estimate)
    if instance.time_spent_seconds and instance.time_spent_seconds > 10:
        minutes = min(instance.time_spent_seconds // 60, 60)
        xp = max(minutes, 1)
        progress.total_xp = (progress.total_xp or 0) + xp
        activity.xp_earned += xp
        activity.minutes_spent += minutes
        activity.stories_read = UserStoryProgress.objects.filter(
            user=user, completed=True
        ).count()

    update_streak(progress)
    progress.save()
    activity.save()


@receiver(post_save, sender=UserQuizAttempt)
def on_quiz_attempt_save(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    progress = get_progress(user)
    activity = get_activity(user)

    progress.total_quiz_attempts += 1

    # XP: 5 XP per correct answer
    xp = (instance.correct_answers or 0) * 5
    progress.total_xp = (progress.total_xp or 0) + xp

    update_streak(progress)
    progress.save()

    activity.quizzes_taken += 1
    activity.xp_earned += xp
    activity.save()