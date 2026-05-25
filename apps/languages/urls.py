from django.urls import path
from .views import LanguageListView, LanguageDetailView, UserTargetLanguagesView, UserTargetLanguageDeleteView

urlpatterns = [
    path('', LanguageListView.as_view(), name='language-list'),
    path('<str:code>/', LanguageDetailView.as_view(), name='language-detail'),
    path('me/', UserTargetLanguagesView.as_view(), name='user-languages'),
    path('me/<str:language_code>/', UserTargetLanguageDeleteView.as_view(), name='user-language-delete'),
]