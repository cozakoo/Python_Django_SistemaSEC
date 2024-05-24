from django.urls import path
from .views import *
from . import views

app_name="alquiler"


urlpatterns = [
    path('',index, name="index"),
    
    # ENCARGADO
    path('encargados/listado',EncargadoListView.as_view(), name="encargado_listar"),
    path('encargados/encargado/crear/',EncargadoCreateView.as_view(), name="encargado_alta"),
    path('encargados/encargado/<int:pk>', EncargadoDetailView.as_view(), name="encargado_detalle"),
    path('encargados/encargado/<int:pk>/editar', EncargadoUpdateView.as_view(), name="encargado_editar"),

    # SERVICIO
    path('servicios/', GestionServicioView.as_view(), name="gestion_servicio"),
    path('servicio/servicio/<int:pk>/', ServicioDetailView.as_view(), name='servicio_detalle'),
    path('aulas/aula/<int:pk>/editar', ServicioUpdateView.as_view(), name="servicio_editar"),
    path('aulas/aula/<int:pk>/eliminar', servicio_eliminar, name="servicio_eliminar"),

    # SALON
    path('salones',SalonesListView.as_view(), name="salon_listar"),
    path('salones/salon/crear/',SalonCreateView.as_view(), name="salon_crear"),
    path('salones/salon/<int:pk>',SalonDetailView.as_view(), name="salon_detalle"),
    path('salones/salon/<int:pk>/editar', SalonUpdateView.as_view(), name="salon_actualizar"),
    path('salones/salon/<int:pk>/eliminar', salon_eliminar, name="salon_eliminar"),

    # ALQUILER
    path('alquileres/',AlquilieresListView.as_view(), name="alquiler_listar"),
    path('alquileres/alquiler/crear',AlquilerCreateView.as_view(), name="alquiler_crear"),
    path('alquileres/alquiler/<int:pk>',AlquilerDetailView.as_view(), name="alquiler_detalle"),
    # path('modificar/<int:pk>', AlquilerUpdateView.as_view(), name="alquiler_actualizar"),
    path('alquileres/alquiler/<int:pk>/agregarlistaespera',agregar_lista_espera, name="agregar_lista_espera"),
    path('alquileres/alquiler/<int:pk>/reemplazarinquilino', reemplazar_inquilino, name="reemplazar_inquilino"),
    path('alquileres/alquiler/<int:alquiler_pk>/listaespera/quitar/<int:afiliado_pk>', quitar_lista_alquiler, name="quitar_lista_alquiler"),

    path('alquileres/alquiler/<int:pk>/eliminar', alquiler_eliminar, name="alquiler_eliminar"),
    
    # PAGO DE ALQUILER
    path('crearPago/',PagoAlquilerCreateView.as_view(), name="pagar_alquiler_crear"),

]