from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.blog.views import ArticleOGView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/blog/", include("apps.blog.api_urls")),
    path("api/accounts/", include("apps.accounts.api_urls")),
    path("articles/<slug:slug>/", ArticleOGView.as_view(), name="article-og"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
