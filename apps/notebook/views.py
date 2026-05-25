from rest_framework import generics, permissions, status, throttling
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import csv
from django.http import HttpResponse
from django.db.models import Q
from .models import UserWord, UserWordCollection
from .serializers import (UserWordSerializer, UserWordCreateSerializer, UserWordReviewSerializer,
                          UserWordCollectionSerializer, UserWordCollectionDetailSerializer, AddRemoveWordSerializer)
from .sm2 import calculate_sm2

class ReviewThrottle(throttling.UserRateThrottle):
    rate = '2000/hour'

class UserWordListView(generics.ListCreateAPIView):
    serializer_class = UserWordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = UserWord.objects.filter(user=self.request.user)
        params = self.request.query_params

        status_filter = params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        is_favorite = params.get('is_favorite')
        if is_favorite in ('true', 'True', '1'):
            qs = qs.filter(is_favorite=True)

        search = params.get('search')
        if search:
            qs = qs.filter(
                Q(word__icontains=search) |
                Q(definition__icontains=search) |
                Q(translation__icontains=search)
            )

        collection = params.get('collection')
        if collection:
            qs = qs.filter(collections__id=collection)

        language = params.get('language')
        if language:
            qs = qs.filter(language__code=language)

        return qs.order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserWordCreateSerializer
        return UserWordSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserWordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserWordSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return UserWord.objects.filter(user=self.request.user)

class UserWordReviewView(generics.GenericAPIView):
    serializer_class = UserWordReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ReviewThrottle]

    def get_queryset(self):
        return UserWord.objects.filter(user=self.request.user)

    def post(self, request, id):
        word = get_object_or_404(UserWord, id=id, user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quality = serializer.validated_data['quality']

        if word.last_reviewed_at and word.next_review_at:
            interval = (word.next_review_at - word.last_reviewed_at).days
        else:
            interval = 0

        ease, interval, reps, next_review = calculate_sm2(
            quality, word.ease_factor, interval, word.times_reviewed
        )

        word.ease_factor = ease
        word.times_reviewed += 1
        word.last_reviewed_at = timezone.now()
        word.next_review_at = next_review

        if quality >= 4 and word.status == 'new':
            word.status = 'learning'
        elif quality >= 4 and word.status == 'learning' and reps >= 2:
            word.status = 'reviewing'
        elif quality >= 4 and word.status == 'reviewing' and reps >= 5:
            word.status = 'mastered'
        elif quality < 3:
            word.status = 'learning'
            word.times_reviewed = max(0, word.times_reviewed - 1)

        word.save()
        return Response({'status': 'review_recorded', 'next_review_at': word.next_review_at})

class DueReviewsView(generics.ListAPIView):
    serializer_class = UserWordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserWord.objects.filter(
            user=self.request.user,
            next_review_at__lte=timezone.now()
        ).exclude(status='mastered')

class ExportNotebookView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        print("=== EXPORT HIT ===")
        print("User:", request.user)
        print("Is authenticated:", request.user.is_authenticated)
        print("Format:", request.query_params.get('format'))
        format_type = request.query_params.get('format', 'json')

        words = UserWord.objects.filter(user=request.user)

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="notebook.csv"'

            writer = csv.writer(response)

            writer.writerow([
                'Word',
                'Definition',
                'Translation',
                'Status',
                'Favorite',
                'Times Reviewed',
            ])

            for word in words:
                writer.writerow([
                    word.word,
                    word.definition,
                    word.translation,
                    word.status,
                    word.is_favorite,
                    word.times_reviewed,
                ])

            return response

        data = UserWordSerializer(words, many=True).data
        return Response(data)

class UserWordCollectionListView(generics.ListCreateAPIView):
    serializer_class = UserWordCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserWordCollection.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserWordCollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserWordCollectionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return UserWordCollection.objects.filter(user=self.request.user)

class AddWordToCollectionView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        collection = get_object_or_404(UserWordCollection, id=id, user=request.user)
        serializer = AddRemoveWordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        word = get_object_or_404(UserWord, id=serializer.validated_data['word_id'], user=request.user)
        collection.words.add(word)
        return Response({'status': 'added'})

class RemoveWordFromCollectionView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        collection = get_object_or_404(UserWordCollection, id=id, user=request.user)
        serializer = AddRemoveWordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        word = get_object_or_404(UserWord, id=serializer.validated_data['word_id'], user=request.user)
        collection.words.remove(word)
        return Response({'status': 'removed'})