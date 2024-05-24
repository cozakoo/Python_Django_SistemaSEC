"""
sec2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from .views import *


handler403 = custom_403_view
urlpatterns = [
    
    #PRINCIPALES
    
    path('', home, name="login"),
    path('admin/', admin.site.urls),
    path('home/', home, name="home"),

    #APLICACIONES
    path('home/app_afiliados/',include('apps.afiliados.urls')),
    path('home/app_cursos/',include('apps.cursos.urls')),
    path('home/app_personas/',include('apps.personas.urls')),
    path('home/app_alquileres/',include('apps.alquileres.urls')),
    path('home/app_reportes/',include('apps.reportes.urls')),

    path('',include('apps.users.urls')),
    path('select2/', include('django_select2.urls')),
    path('selectable/', include('selectable.urls')),

    path('manual_usuario/', abrirManualUsuario, name="manual_usuario"),
    path('documentacion_tecnica/', abrirDocumentacionTecnica, name="documentacion_tecnica"),


]


