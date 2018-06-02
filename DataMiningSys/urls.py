"""DataMiningSys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from DMAS import views
from DMAS.programs import api

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    #以下为页面连接
    url(r'^$', views.index,name='index'),
    url(r'^login/$',views.login,name='login'),
    url(r'^dashboard/$',views.dashboard,name='dashboard'),
    url(r'^stockInfo/$',views.stockInfo,name='stockInfo'),
    url(r'^incInfo/$',views.incInfo,name='incInfo'),
    url(r'^cancelInfo/$',views.cancelInfo,name='cancelInfo'),
    url(r'^tmpjs/$',views.tmpjs,name='tmpjs'),

    #以下为API连接
    url(r'^apis/$',api.apis,name='apis'),
    url(r'^download/(?P<filename>\w+\.\w{3,4})/$',views.download,name='download')
]
