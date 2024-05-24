from django.shortcuts import render
from django.contrib.auth import logout as django_logout, login as django_login, authenticate
from apps.afiliados.models import RelacionFamiliar

from apps.alquileres.models import Alquiler
from apps.personas.models import Rol
from sec2 import settings
from utils.funciones import mensaje_advertencia

from sec2.utils import get_filtro_roles, get_selected_rol_pk, redireccionarDetalleRol
from utils.funciones import mensaje_advertencia

from apps.personas.forms import RolFilterForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from django.contrib.auth.models import User
    

from django.http import HttpResponse, FileResponse
from django.conf import settings
import os

def custom_403_view(request, exception):
    return render(request, '403.html', {}, status=403)



def obtener_permisos_user_string(user):
    permisos = user.user_permissions.all()
    nombres_permisos = [permiso.codename for permiso in permisos]
    return nombres_permisos
        # Imprimir los nombres de los permisos



def cambiar_estado_alquileres():
    alquileres = Alquiler.objects.filter(estado=1, fecha_alquiler__lt=datetime.now())
    alquileres_hoy = Alquiler.objects.filter(estado=1, fecha_alquiler__date=date.today())

    for alquiler in alquileres:
        alquiler.estado = 3  # Cambiar estado a "Finalizado"
        alquiler.save()

    # for alquiler_hoy in alquileres_hoy:
    #     alquiler_hoy.estado = 2  # Cambiar estado a "En curso"
    #     alquiler_hoy.save()
    

def revisarGrupoFamiliar(request):
    
    """Chequear si algún grupo familiar que sea hijo es mayor de edad"""
    # Filtrar roles sin fecha de finalización (hasta)
    roles_sin_fecha_hasta = Rol.objects.filter(hasta__isnull=True)

    # Filtrar relaciones familiares tipo 2 relacionadas con roles sin fecha de finalización
    relaciones_tipo_2 = RelacionFamiliar.objects.filter(tipo_relacion=2, familiar__in=roles_sin_fecha_hasta)

    for relacion in relaciones_tipo_2:
        if relacion.familiar.persona.es_mayor_edad: 
           mensaje_advertencia(request, f"Atencion! El familiar con el DNI: {relacion.familiar.persona.dni} es mayor de edad"  )

    

@login_required(login_url='/login/')
def home(request):
    cambiar_estado_alquileres()
    """Chequear si algún grupo familiar que sea hijo es mayor de edad"""
    permisos = obtener_permisos_user_string(request.user)
    revisarGrupoFamiliar(request)

    filter_rol = get_filtro_roles(request)
    rol = get_selected_rol_pk(filter_rol)
    
    if rol is not None:
        return redireccionarDetalleRol(rol)
    contexto = dict() 
    
    contexto['filter_form'] = filter_rol
    contexto['permisos'] =permisos
    
    
    return render(request, 'home.html', contexto)

from django.http import FileResponse
import os
@login_required(login_url='/login/')
def abrir_pdf(request, nombre_archivo, nombre_mostrado):
    # Ruta al archivo PDF en tu sistema
    ruta_pdf = os.path.join(settings.BASE_DIR, '..', 'documentacion', nombre_archivo)

    try:
        if os.path.exists(ruta_pdf):
            response = FileResponse(open(ruta_pdf, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{nombre_mostrado}"'
            return response
        else:
            return HttpResponse('El archivo PDF no se encontró.', status=404)
    except Exception as e:
        return HttpResponse(f'Error al abrir el archivo PDF: {str(e)}', status=500)

@login_required(login_url='/login/')
def abrirManualUsuario(request):
    return abrir_pdf(request, 'manual_de_usuario.pdf', 'manual_de_usuario.pdf')

@login_required(login_url='/login/')
def abrirDocumentacionTecnica(request):
    return abrir_pdf(request, 'documento_tecnico.pdf', 'documento_tecnico.pdf')