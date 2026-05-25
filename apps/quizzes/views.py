from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Quiz, UserQuizAttempt
from .serializers import QuizDetailSerializer, QuizAttemptSerializer, UserQuizAttemptSerializer
from apps.stories.models import Story

class StoryQuizzesView(generics.ListAPIView):
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        story = get_object_or_404(Story, slug=self.kwargs['slug'])
        return Quiz.objects.filter(story=story)

class QuizAttemptView(generics.CreateAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        story = get_object_or_404(Story, slug=slug)
        version_type = request.data.get('version_type', 'original')
        quiz = get_object_or_404(Quiz, story=story, version_type=version_type)
        if quiz.is_premium and not request.user.is_premium:
            return Response({'error': 'Premium quiz'}, status=status.HTTP_402_PAYMENT_REQUIRED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data['answers']
        time_taken = serializer.validated_data['time_taken_seconds']

        def normalize(val):
            val = val.strip().lower()
            return {"true": "yes", "false": "no"}.get(val, val)

        questions = quiz.questions.all()
        correct = 0
        question_results = []
        for q in questions:
            user_answer = answers.get(str(q.id), '')
            is_correct = normalize(user_answer) == normalize(q.correct_answer)
            if is_correct:
                correct += 1
            question_results.append({
                'question_id': q.id,
                'selected_answer': user_answer,
                'correct_answer': q.correct_answer,
                'is_correct': is_correct,
                'explanation': q.explanation or '',
            })

        score = (correct / len(questions)) * 100 if questions else 0
        attempt = UserQuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            correct_answers=correct,
            total_questions=len(questions),
            answers=answers,
            time_taken_seconds=time_taken
        )

        from apps.stories.models import UserStoryProgress
        progress, _ = UserStoryProgress.objects.get_or_create(user=request.user, story=story)
        if score > progress.quiz_best_score:
            progress.quiz_best_score = score
            progress.save()

        return Response({
            'attempt_id': attempt.id,
            'score': score,
            'correct_answers': correct,
            'total_questions': len(questions),
            'answers': question_results,
        })

class QuizHistoryView(generics.ListAPIView):
    serializer_class = UserQuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserQuizAttempt.objects.filter(user=self.request.user).order_by('-created_at')