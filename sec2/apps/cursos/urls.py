
from django.urls import path
from .views.actividad_views import *
from .views.curso_views import *
from .views.dictado_views import *
from .views.horario_views import *
from .views.clase_views import *
from .views.profesor_views import *
from .views.alumno_views import *
from .views.aula_views import *
from .views.pago_views import *
from .views.views import *

app_name="cursos"

urlpatterns = [
    # PRINCIPAL
    path('',index, name="index"),

    # ACTIVIDADES
    path('actividades/', GestionActividadView.as_view(), name="gestion_actividad"),
    path('actividades/actividad/<int:pk>', ActividadDetailView.as_view(), name="actividad_detalle"),
    path('actividades/actividad/<int:pk>/editar', ActividadUpdateView.as_view(), name="actividad_editar"),
    path('actividades/actividad/<int:pk>/eliminar', actividad_eliminar, name="actividad_eliminar"),

    # AULAS
    path('aulas/', GestionAulaView.as_view(), name="gestion_aula"),
    path('aulas/aula/<int:pk>/', AulaDetailView.as_view(), name='aula_detalle'),
    path('aulas/aula/<int:pk>/editar', AulaUpdateView.as_view(), name="aula_editar"),
    path('aulas/<int:pk>/eliminar', aula_eliminar, name="aula_eliminar"),

    # PROFESOR
    path('profesores', ProfesorListView.as_view(), name="profesor_listado"),
    path('profesores/profesor/crear', ProfesorCreateView.as_view(), name="profesor_crear"),
    path('profesores/profesor/<int:pk>', ProfesorDetailView.as_view(), name="profesor_detalle"),
    path('profesores/profesor/<int:pk>/editar', ProfesorUpdateView.as_view(), name="profesor_editar"),
    path('profesores/profesor/<int:pk>/eliminar', profesor_eliminar, name="profesor_eliminar"),

    # CURSOS
    path('cursos/listado', CursoListView.as_view(), name="curso_listado"),
    path('cursos/curso/crear/', CursoCreateView.as_view(), name="curso_crear"),
    path('cursos/curso/<int:pk>', CursoDetailView.as_view(), name="curso_detalle"),
    path('cursos/curso/<int:pk>/editar', CursoUpdateView.as_view(), name="curso_editar"),
    path('cursos/curso/<int:pk>/eliminar', curso_eliminar, name="curso_eliminar"),
    path('cursos/curso/<int:pk>/listaespera', cursoListaEspera, name="curso_lista_espera"),
    path('cursos/curso/<int:pk>/listaespera/rol/<int:rol_pk>/<str:accion>/', gestionListaEspera, name="gestion_lista_espera"),
    
    # GESTION DE LISTA DE ESPERA
    path('cursos/curso/<int:pk>/listaespera/alumnopotencial/inscribir', AlumnoPotencialCreateView.as_view(), name="alumno_nuevo_lista_espera"),

    ## VERIFICAR Y BUSCAR PERSONA ANTES DE PROCEDER A LA INSCRIPCION
    path('cursos/curso/<int:curso_pk>/verificarpersona', VerificarInscripcionView.as_view(), name="verificar_persona"),
    path('buscar-persona/', BuscarPersonaView.as_view(), name='buscar_persona'),

    # DICTADOS (accedido desde cursos)
    path('cursos/curso/<int:pk>/dictados/dictado/crear', DictadoCreateView.as_view(), name="dictado_crear"),
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>', DictadoDetailView.as_view(), name="dictado_detalle"),
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/editar', DictadoUpdateView.as_view(), name="dictado_editar"),
    
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/finalizar', finalizarDictado , name="dictado_finalizar"),

    # HORARIO (accedido desde dictado)
    path('curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/horarios/horario/crear/', HorarioCreateView.as_view(), name='horario_crear'),
    path('curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/horarios/horario/<int:horario_pk>/elminar', eliminarHorario, name='horario_eliminar'),

    # ASIGNACIÓN DE AULA (accedido desde el horario)
    path('curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/horarios/horario/<int:horario_id>/vincularAula/', asignar_aula, name='asignar_aula'),

    # CLASE (accedido desde dictaod)
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_id>/generarclaeses/', generar_clases, name="generar_clases"),
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/clases/clase/<int:clase_pk>', ClaseDetailView.as_view(), name="clase_detalle"),
    
    # ALUMNO (accedido desde el dictado)

    #CONTROL DE ASISTENCIA
    path('marcar_asistencia/Alumno/<int:clase_id>/', marcar_asistencia, name='generar_asistencia'),

    #ALUMNNOS POR CURSO
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/Alumnos', AlumnosEnDictadoList.as_view(), name="alumno_inscripto"),

    # GESTION DE INSCRIPCION
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/<str:tipo>/<int:persona_pk>/Incripcion/<str:accion>/', gestionInscripcion, name="gestion_inscripcion"),
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/AlumnoNuevo/inscribir', AlumnoCreateView.as_view(), name="alumno_nuevo_inscribir"),

    path('alumnos', AlumnosListView.as_view(), name="alumnos_listado"),
    path('alumnos/alumnno/<int:pk>/', AlumnoDetailView.as_view(), name="alumno_detalle"),
    path('alumnos/alumno/<int:pk>/eliminar', alumno_eliminar, name="alumno_eliminar"),

    #GENERAR PDF
    path('generar-pdf-afiliado-dictado/<int:dictado_pk>/<int:persona_pk>', generarPDF_Afiliado , name="generar_pdf_dictado_finalizado_afiliado"),
    
    #NO SE UTILIZARIA
    path('cursos/curso/<int:curso_pk>/dictados/dictado/<int:dictado_pk>/Alumnos/listaEspera', listaEspera , name="dictado_lista_espera"),
    path('pago/listado/profesor', PagoProfesorListView.as_view() ,name="pago_cuota_profesor_listado"),
    path('pago/profesor/crear', PagoProfesorCreateView.as_view(), name="pago_profesor"),
    path('pago/profesor/<int:pk>', PagoProfesorDetailView.as_view(), name="pago_profesor_detalle"),
    path('get_dictados_por_titular/<int:titular_pk>/', get_dictados_por_titular, name='get_dictados_por_titular'),

    path('pago/listado/alumno', PagoAlumnoListView.as_view() ,name="pago_cuota_alumno_listado"),
    path('pago/obtenerDictadosEnCurso/<int:pk>', obtenerDictadosEnCurso ,name="obtenerDictadoEnCurso"),

    path('pago/alumno/crear', PagoAlumnoCreateView.as_view(), name="pago_alumno_crear"),
    path('pago/alumno/<int:pk>', PagoAlumnoDetailView.as_view(), name="pago_alumno_detalle"),

    path('get_dictados_por_alumno/<int:rol_pk>/', get_dictados_por_alumno, name='get_dictados_por_alumno'),
]
