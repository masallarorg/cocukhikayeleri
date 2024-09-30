"""
URL configuration for cocukhikayeleri project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from stories.sitemap import StorySitemap  # 'stories' uygulamasındaki sitemap'ı import edin
from django.contrib.sitemaps.views import sitemap

from django.views.generic import TemplateView
sitemaps = {
    'stories': StorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include('stories.urls')),  # stories uygulamasındaki URL'leri kullan
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
