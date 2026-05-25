from datetime import timedelta
from django.utils import timezone

def calculate_sm2(quality, ease_factor, interval, repetitions):
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1

    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < 1.3:
        ease_factor = 1.3

    next_review = timezone.now() + timedelta(days=interval)
    return ease_factor, interval, repetitions, next_review