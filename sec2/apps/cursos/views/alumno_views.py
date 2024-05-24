# from ..models import Alumno
from multiprocessing import context
from pyexpat.errors import messages
import uuid

from django.http import HttpResponse
from apps.afiliados.models import Afiliado, Familiar
from apps.afiliados.views import existe_persona_activa, redireccionar_detalle_rol

from apps.cursos.models import Clase
from apps.personas.models import Rol
from utils.funciones import mensaje_advertencia, mensaje_error, mensaje_exito

from ..forms.alumno_forms import *
from ..forms.curso_forms import *
from ..forms.dictado_forms import *
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from sec2.utils import ListFilterView, get_filtro_roles, get_selected_rol_pk
from django.shortcuts import redirect
from utils.constants import *
from django.contrib import messages
from django.urls import reverse
import datetime
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required , login_required 

# ---------------- ALUMNO CREATE ----------------
class AlumnoCreateView(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    """
    CREAR TTUTOR LEGAL EN EL CASO DE QUE SEA MENOR DE EDAD
    """
    model = Persona
    form_class = AlumnoPersonaForm
    template_name = 'alumno/alumno_form.html'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'


    def get_success_url(self):
        curso_pk = self.kwargs.get('curso_pk')
        dictado_pk = self.kwargs.get('dictado_pk')
        return reverse_lazy('cursos:persona_inscribir', kwargs={'curso_pk': curso_pk, 'dictado_pk': dictado_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso_pk = self.kwargs.get('curso_pk')
        dictado_pk = self.kwargs.get('dictado_pk')
        context['unique_identifier'] = f'alumno_form_{uuid.uuid4().hex}'
        dictado = get_object_or_404(Dictado, curso__pk=curso_pk, pk=dictado_pk)
        context['titulo'] = f'Inscripción para {dictado.curso.nombre}'
        return context

    def form_valid(self, form):
        dni = form.cleaned_data["dni"]
        persona_existente = Persona.objects.filter(dni=dni).first()
        
        if persona_existente:
            messages.error(self.request, f'La persona ya está registrada en el sistema.')
            form = AlumnoPersonaForm(self.request.POST)
            return super().form_invalid(form)
        else:            
            # La instancia de Alumno no existe, crear una nueva instancia
            persona = Persona(
                dni=dni,
                cuil=form.cleaned_data["cuil"],
                nombre=form.cleaned_data["nombre"],
                apellido=form.cleaned_data["apellido"],
                fecha_nacimiento=form.cleaned_data["fecha_nacimiento"],
                mail=form.cleaned_data["mail"],
                celular=form.cleaned_data["celular"],
                estado_civil=form.cleaned_data["estado_civil"],
                nacionalidad=form.cleaned_data["nacionalidad"],
                direccion=form.cleaned_data["direccion"],
                es_alumno = True
            )
            persona.save()
            # Crear una nueva instancia de Alumno
            alumno = Alumno(
                persona=persona,
                tipo = Alumno.TIPO
            )
            alumno.save()
            curso_pk = self.kwargs.get('curso_pk')
            dictado_pk = self.kwargs.get('dictado_pk')
            dictado = get_object_or_404(Dictado, curso__pk=curso_pk, pk=dictado_pk)
            dictados_seleccionados = form.cleaned_data.get("dictados", [])
            # Agregar el alumno a los dictados seleccionados
            alumno.dictados.add(dictado)
            # Agregar el mensaje de éxito para mostrar en el template
            messages.success(self.request, f'{ICON_CHECK} Alumno inscrito al curso exitosamente!. Cierre la ventana y recargue el detalle del dictado')
            return redirect(reverse('cursos:verificar_persona', kwargs={'curso_pk': curso_pk, 'dictado_pk': dictado_pk}))
        
    def form_invalid(self, form):
        messages.warning(self.request, f'Corrige los errores en el formulario.')
        return super().form_invalid(form)

# ---------------- ALUMNO CREATE ----------------
class AlumnoPotencialCreateView(LoginRequiredMixin, PermissionRequiredMixin ,CreateView):
    model = Persona
    form_class = AlumnoPersonaForm
    template_name = 'alumno/alumno_form.html'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        return reverse_lazy('cursos:persona_inscribir', kwargs={'pk': pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['unique_identifier'] = f'alumno_form_{uuid.uuid4().hex}'

        curso = get_object_or_404(Curso, pk=pk)
        context['titulo'] = f'Inscripción para {curso.nombre}'
        return context

    def form_valid(self, form):
        dni = form.cleaned_data["dni"]

        if existe_persona_activa(self, dni):
            mensaje_error(self.request, f'{MSJ_PERSONA_EXISTE}')
            form = AlumnoPersonaForm(self.request.POST)
            return super().form_invalid(form)
        else:
            persona = Persona(
                dni=dni,
                cuil=form.cleaned_data["cuil"],
                nombre= form.cleaned_data["nombre"].title(),
                apellido=form.cleaned_data["apellido"].title(),
                fecha_nacimiento=form.cleaned_data["fecha_nacimiento"],
                mail=form.cleaned_data["mail"],
                celular=form.cleaned_data["celular"],
                estado_civil=form.cleaned_data["estado_civil"],
                nacionalidad=form.cleaned_data["nacionalidad"],
                direccion=form.cleaned_data["direccion"],
                es_alumno = True
            )
            persona.save()

            current_datetime = timezone.now()

            # Crear una nueva instancia de Alumno
            alumno = Alumno(
                persona=persona,
                tipo = Alumno.TIPO,
                desde = current_datetime,
            )
            alumno.save()

            # Agregar el alumno a los dictados seleccionados en el formulario
            pk = self.kwargs.get('pk')

            curso = get_object_or_404(Curso, pk=pk)
            rol = get_object_or_404(Rol, persona=persona)

            lista_espera_instance = ListaEspera(curso=curso, rol=rol)
            lista_espera_instance.save()
            curso.lista_espera.add(lista_espera_instance)
            curso.save
            mensaje_exito(self.request, f'{MSJ_LISTAESPERA_AGREGADO}')
            detail_url = reverse('cursos:verificar_persona', kwargs={'curso_pk': pk,})
            return redirect(detail_url)
        
    def form_invalid(self, form):
        mensaje_advertencia(self.request, f'{MSJ_CORRECTION}')
        return super().form_invalid(form)
    
#------------ LISTADO DE ALUMNOS DADO UN DICTADO --------------
from django.views.generic import ListView

class AlumnosEnDictadoList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Alumno
    paginate_by = 100
    template_name = 'dictado/dictado_alumnos.html'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_queryset(self):
        # Obtener todos los alumnos sin filtrar por dictado
        queryset = Alumno.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'LISTA DE TODOS LOS ALUMNOS'
        return context

def marcar_asistencia(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    
    # Verificar si la clase actual es la primera clase del dictado
    es_primera_clase = not Clase.objects.filter(
        reserva__horario__dictado=clase.reserva.horario.dictado,
        reserva__fecha__lt=clase.reserva.fecha
    ).exists()

    # Verificar si la clase actual es la última clase del dictado
    es_ultima_clase = not Clase.objects.filter(
        reserva__horario__dictado=clase.reserva.horario.dictado,
        reserva__fecha__gt=clase.reserva.fecha
    ).exists()

    if not es_primera_clase:
        if not es_ultima_clase:
            # La clase no es la primera, entonces verificamos la asistencia de la clase anterior
            clase_anterior = Clase.objects.filter(
                reserva__horario__dictado=clase.reserva.horario.dictado,
                reserva__fecha__lt=clase.reserva.fecha
            ).last()

            if not clase_anterior or not clase_anterior.asistencia_tomada:
                # La asistencia de la clase anterior no se ha tomado, mostrar un mensaje de error
                messages.error(request, f'{ICON_ERROR} La asistencia de la clase anterior no se ha tomado.')
                return redirect('cursos:clase_detalle', curso_pk=clase.reserva.horario.dictado.curso.pk, dictado_pk=clase.reserva.horario.dictado.pk, clase_pk=clase.pk)
        else:
            #Codigo para cucando sea la ultima clase
            #Se cambia el estado del dictado
            clase.reserva.horario.dictado.estado = 3
            clase.reserva.horario.dictado.fecha_fin = clase.reserva.fecha
            clase.reserva.horario.dictado.save()
    else:
        #Codigo para cuando sea la primer clase
        #Se cambia el estado del dictado
        clase.reserva.horario.dictado.estado = 2
        clase.reserva.horario.dictado.save()
    
    if request.method == 'POST':
        # ------------- ASISTENCIA PARA INSCRITOS
        alumnos_asistencia_ids = request.POST.getlist('alumnos_asistencia')

        # Obtengo los objeros de las asistencias
        alumnos_asistencia = Alumno.objects.filter(id__in=alumnos_asistencia_ids)
        afiliado_asistencia = Afiliado.objects.filter(id__in=alumnos_asistencia_ids)
        familiar_asistencia = Familiar.objects.filter(id__in=alumnos_asistencia_ids)
        profesor_asistencia_inscripto = Profesor.objects.filter(id__in=alumnos_asistencia_ids)
        
        #unifico mis objetos en una lista: FALTA LA ASISTENCIA DEL FAMILIAR
        lista_asistencia = list(alumnos_asistencia) + list(afiliado_asistencia) + list(familiar_asistencia) + list(profesor_asistencia_inscripto)        
        # lista_asistencia = list(alumnos_asistencia) + list(afiliado_asistencia) +  list(profesor_asistencia_inscripto)        
        clase.asistencia.set(lista_asistencia)

        # ------------- ASISTENCIA PARA PROFESOR(ES)
        # para el titular
        profesor_asistencia_ids = request.POST.getlist('profesor__asistencia')
        profesor_titular = Profesor.objects.filter(id__in=profesor_asistencia_ids)
        clase.asistencia_profesor.set(profesor_titular)

        clase.asistencia_tomada = True
        clase.save()

        messages.success(request, f'{ICON_CHECK} Asistencia tomada correctamente.')
        return redirect('cursos:dictado_detalle', curso_pk=clase.reserva.horario.dictado.curso.pk, dictado_pk=clase.reserva.horario.dictado.pk)

    messages.error(request, f'{ICON_ERROR} Ha ocurrido un error inesperado.')
    return redirect('cursos:clase_detalle', curso_pk=clase.reserva.horario.dictado.curso.pk, dictado_pk=clase.reserva.horario.dictado.pk, clase_pk=clase.pk)

#------------ LISTADO DE TODOS MIS ALUMNOS  --------------
class AlumnosListView(LoginRequiredMixin,PermissionRequiredMixin, ListFilterView):
    model = Alumno
    paginate_by = MAXIMO_PAGINATOR
    filter_class = AlumnoFilterForm
    template_name = 'alumno/alumno_listado.html'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form = AlumnoFilterForm(self.request.GET)
        context['filtros'] = filter_form
        context['titulo'] = "Listado de Alumnos "
        context['filter_form'] = get_filtro_roles(self.request)

        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
    
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     dni = self.request.GET.get('dni')
    #     print("dni", dni)
    #     apellido = self.request.GET.get('apellido')
    #     return queryset

##--------------- ALUMNO DETALLE --------------------------------
from django.views.generic import DetailView

class AlumnoDetailView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    model = Alumno
    template_name = 'alumno/alumno_detalle.html'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'
    
    def get_context_data(self, **kwargs):
        rol = get_object_or_404(Rol, persona__pk=self.object.persona.pk)
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Detalle del alumno"
        context['rol'] = rol
        context['tituloListado'] = 'Dicados Inscriptos'
        context['filter_form'] = get_filtro_roles(self.request)
        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)

def alumno_eliminar(request, pk):
    alumno = get_object_or_404(Alumno,pk=pk)
    print("alumno",alumno)
    dictados_en_estado_2 = alumno.dictados.filter(estado=2).exists()
    if dictados_en_estado_2:
        mensaje_error(request, "El alumno esta inscrito en dictados que no han finalizado.")
    else:
        rol = get_object_or_404(Rol, persona__pk=alumno.persona.pk)
        alumno.darDeBaja()
        mensaje_exito(request, f'Alumno dado de baja con exito')
    return redirect('cursos:alumno_detalle', pk=alumno.pk)