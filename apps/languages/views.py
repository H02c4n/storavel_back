from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Language, UserTargetLanguage
from .serializers import LanguageSerializer, UserTargetLanguageSerializer

class LanguageListView(generics.ListAPIView):
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]

class LanguageDetailView(generics.RetrieveAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    lookup_field = 'code'
    permission_classes = [permissions.AllowAny]

class UserTargetLanguagesView(generics.ListCreateAPIView):
    serializer_class = UserTargetLanguageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserTargetLanguage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserTargetLanguageDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'language_code'

    def get_queryset(self):
        return UserTargetLanguage.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        language_code = kwargs.get('language_code')
        try:
            language = Language.objects.get(code=language_code)
            obj = UserTargetLanguage.objects.get(user=request.user, language=language)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (Language.DoesNotExist, UserTargetLanguage.DoesNotExist):
            return Response({'error': 'Language not found in user targets'}, status=status.HTTP_404_NOT_FOUND)