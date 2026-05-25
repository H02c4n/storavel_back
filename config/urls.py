from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
path('admin/', admin.site.urls),
path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
path('api/auth/', include('apps.accounts.urls')),
path('api/languages/', include('apps.languages.urls')),
path('api/stories/', include('apps.stories.urls')),
path('api/vocabulary/', include('apps.vocabulary.urls')),
path('api/notebook/', include('apps.notebook.urls')),
path('api/quizzes/', include('apps.quizzes.urls')),
path('api/progress/', include('apps.progress.urls')),
]