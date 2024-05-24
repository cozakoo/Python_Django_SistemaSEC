from django.shortcuts import render
from .views import CustomLoginView, CreacionUsuarios,cerrar_session, UserListView, actualizar_permisos
from django.urls import path

app_name = "users"

urlpatterns = [
  path('login/', CustomLoginView.as_view(), name='login'),
  path('registrar_usuarios/', CreacionUsuarios.as_view(), name='user_register'),
  path('listar_usuarios/', UserListView.as_view(), name='user_listado'),
  path('actualizar_permisos/<int:pk>',actualizar_permisos,name="actualizar_permisos"),
  path('cerrar_session/',cerrar_session,name='cerrar_session'),

   ]