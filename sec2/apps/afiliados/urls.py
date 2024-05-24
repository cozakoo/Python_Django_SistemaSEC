# Importaciones del sistema
from django.urls import path
# Importaciones locales
from selectable import urls as selectable_urls
from .views import *
from django.contrib.auth.decorators import login_required, permission_required



app_name = "afiliados"

urlpatterns = [
    path('',index, name="index"),

    #AFILIADO
    path('afiliados/afiliado/crear/',AfiliadoCreateView.as_view(), name="afiliado_crear"),
    path('afiliados/afiliado/<int:pk>',AfiliadoDetailView.as_view(), name="afiliado_detalle"),
    path('afiliados/afiliado/<int:pk>/editar', AfiliadoUpdateView.as_view(), name="afiliado_actualizar"),
    path('afiliados/listar',AfiliadosListView.as_view(), name="afiliado_listar"),
    path('afiliados/afiliado/<int:pk>/<str:accion>/<str:origen>/', afiliado_afiliar_desafiliar, name="afiliado_afiliar_desafiliar"),
    #ALTA GRUPO FAMILIAR (accedido desde afiliado)
    path('afiliado/<int:pk>/grupoFamiliar/crear', FamiliaCreateView.as_view(), name="crear_familiar"),

    #RELACION AFILIADO-GRUPO FAMILIAR
    path('grupofamiliar/listado', RelacionFamiliarListView.as_view(), name="grupo_familiar_listar"),

    #GRUPO FAMILIAR
    path('grupofamiliar/crear', alta_familiar, name="crear_familiar_directo"),
    path('afiliado/<int:pk>/grupoFamiliar/familia/<int:familiar_pk>', FamiliarDetailView.as_view(), name="familiar_detalle"),
    path('afiliado/<int:pk>/grupoFamiliar/familia/<int:familiar_pk>/editar/', FamiliarUpdateView.as_view(), name="familiar_editar"),
    path('afiliado/<int:pk>/grupoFamiliar/familia/<int:familiar_pk>/eliminar', familiar_eliminar, name="familiar_eliminar"),

    # path('afiliado/grupoFamiliar/familia/<int:familiar_pk>/editar', FamiliarUpdateView_.as_view(), name="familiar_editar_"),
    #ACCEDIDOS DESDE LA APLICACION DE CURSOS
    # path('afiliado/grupoFamiliar/familia/<int:familiar_pk>', FamiliarDetailVentanaNuevaView_.as_view(), name="familiar_detalle_"),

    #GENERAR PDF
    path('pago/afiliado/afiliado/<int:pk>/generarnota', confeccionarNota ,name="confeccionar_nota"),
    path('pago/afiliado/cuotas', PagoCuotaCreateView.as_view() ,name="pagar_cuota_sindical"),
    
    path('pago/listado', PagoCuotaListView.as_view() ,name="pago_cuota_listado"),
    path('pago/ruta_para_actualizar_afiliados/', obtener_afiliados_por_cuit_empleador, name='ruta_para_actualizar_afiliados'),
    
    path('pago/afiliado/actualizar', cuota_sindical_actualizar_estado ,name="actualizar_estado"),
 
]