"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls import include, url
from rest_framework_jwt.views import (
    obtain_jwt_token
    , refresh_jwt_token
    , verify_jwt_token
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth
    url(r'^api/obtain-token/?', obtain_jwt_token),
    url(r'^api/refresh-token/?', refresh_jwt_token),
    url(r'^api/verify-token/?', verify_jwt_token),

    # API
    url(r'^api/', include('stock_simulator.urls'))
]
