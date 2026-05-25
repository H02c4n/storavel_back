from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Story, StoryVersion, UserStoryProgress, UserNote
from .serializers import StoryListSerializer, StoryDetailSerializer, StoryVersionSerializer, UserStoryProgressSerializer, UserNoteSerializer, StoryWordSerializer
from apps.vocabulary.models import StoryWord

class StoryListView(generics.ListAPIView):
    queryset = Story.objects.filter(is_published=True)
    serializer_class = StoryListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['language__code', 'level_min', 'level_max', 'story_type', 'tags__slug']
    search_fields = ['title']
    ordering_fields = ['order', 'title', 'level_min', 'estimated_read_minutes']

class StoryDetailView(generics.RetrieveAPIView):
    queryset = Story.objects.filter(is_published=True)
    serializer_class = StoryDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

class StoryVersionListView(generics.ListAPIView):
    serializer_class = StoryVersionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        story = get_object_or_404(Story, slug=self.kwargs['slug'])
        return story.versions.all()

class StoryVersionDetailView(generics.RetrieveAPIView):
    serializer_class = StoryVersionSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        story = get_object_or_404(Story, slug=self.kwargs['slug'])
        return get_object_or_404(StoryVersion, story=story, version_type=self.kwargs['version_type'])

class StoryWordsView(generics.ListAPIView):
    serializer_class = StoryWordSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        story = get_object_or_404(Story, slug=self.kwargs['slug'])
        return StoryWord.objects.filter(story=story).select_related('word').order_by('order')

class UserStoryProgressView(generics.RetrieveUpdateAPIView):
    serializer_class = UserStoryProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        story = get_object_or_404(Story, slug=self.kwargs['slug'])
        obj, _ = UserStoryProgress.objects.get_or_create(user=self.request.user, story=story)
        return obj

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Accumulate time instead of overwriting
        new_time = request.data.get('time_spent_seconds')
        if new_time:
            instance.time_spent_seconds += int(new_time)

        # Track version read
        version_read = request.data.get('version_read')
        if version_read:
            instance.last_version_read = version_read
            versions_read = instance.versions_read or []
            if version_read not in versions_read:
                versions_read.append(version_read)
                instance.versions_read = versions_read

        # Mark completed if read_count incremented or explicitly set
        if request.data.get('completed'):
            instance.completed = True

        # Auto-increment read_count on each progress update with time
        # Frontend already filters by min reading time, so any time > 0 counts
        if new_time and int(new_time) > 0:
            instance.read_count += 1
            if not instance.completed:
                instance.completed = True

        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class UserNoteView(generics.RetrieveUpdateAPIView):
    serializer_class = UserNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        story = get_object_or_404(Story, slug=self.kwargs['slug'])
        obj, _ = UserNote.objects.get_or_create(user=self.request.user, story=story)
        return obj