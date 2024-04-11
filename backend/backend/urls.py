"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from business.api.auth import login, signup, testLogin, logout, userInfo
from business.api.userInteraction import like_paper, score_paper, collect_paper
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login", login),
    path("api/signup", signup),
    path("api/testLogin", testLogin),
    path("api/logout", logout),
    path("api/userInfo", userInfo),
    path("api/likePaper", like_paper),
    path("api/scorePaper", score_paper),
    path("api/collectPaper", collect_paper),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
