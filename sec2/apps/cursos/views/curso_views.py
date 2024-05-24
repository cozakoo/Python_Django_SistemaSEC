from django.shortcuts import get_object_or_404, redirect
from apps.afiliados.models import Afiliado, Familiar
from apps.afiliados.views import redireccionar_detalle_rol
from apps.alquileres.models import Encargado
from apps.cursos.forms.actividad_forms import ActividadForm
from apps.cursos.models import Alumno, Clase, Curso, DetallePagoAlumno, DetallePagoProfesor, Dictado, PagoAlumno, PagoProfesor, Profesor, Titular
from apps.personas.models import Persona, Rol
from utils.funciones import mensaje_advertencia, mensaje_error, mensaje_exito
from ..forms.curso_forms import *
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from sec2.utils import ListFilterView, get_filtro_roles, get_selected_rol_pk
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required , login_required 
from django.utils import timezone

#--------------- CREATE DE CURSOS--------------------------------
class CursoCreateView(LoginRequiredMixin, PermissionRequiredMixin,CreateView):
    model = Curso
    form_class = CursoForm
    success_url = reverse_lazy('cursos:curso_crear')
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo_curso = self.request.GET.get('tipo', None)
        context['filter_form'] = get_filtro_roles(self.request)

        if tipo_curso == 'sec':
            context['titulo'] = "Alta de Curso del SEC 2"
        elif tipo_curso == 'convenio':
            context['titulo'] = "Alta de Convenio"
        elif tipo_curso == 'actividad':
            context['titulo'] = "Alta de Gimnasia"
        else:
            context['titulo'] = "Tipo de Curso"  # Default title
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tipo_curso = self.request.GET.get('tipo', None)
        kwargs['initial'] = {'tipo_curso': tipo_curso}
        return kwargs
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        tipo_curso = self.request.GET.get('tipo', None)
        if tipo_curso == 'sec':
            self.template_name = 'curso/curso_alta_sec.html'
        elif tipo_curso == 'convenio':
            self.template_name = 'curso/curso_alta_convenio.html'
        elif tipo_curso == 'actividad':
            self.template_name = 'curso/curso_alta_gimnasio.html'
        else:
            self.template_name = 'curso/seleccion_tipo_curso.html'

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        tipo_curso = self.request.GET.get('tipo', None)
        # Actualizar el valor de es_convenio en base al tipo de curso
        if tipo_curso == 'convenio':
            form.instance.es_convenio = True
        else:
            form.instance.es_convenio = False
        # Guardar el formulario
        # form.instance.actividad = actividad
        result = super().form_valid(form)
        
        form.instance.actividad = form.cleaned_data['actividad']
        form.instance.descripcion = form.cleaned_data['descripcion'].capitalize()
        form.instance.cupo_estimativo = form.cleaned_data['cupo_estimativo']
        form.instance.precio_total = form.cleaned_data['precio_total']
        form.instance.precio_estimativo_profesor = form.cleaned_data['precio_estimativo_profesor']

        # form.instance.descripcion = form.cleaned_data['descripcion'].capitalize()
        form.instance.nombre = form.cleaned_data['nombre'].title()
        form.save()
        messages.success(self.request, f'{ICON_CHECK} Alta de curso exitosa!')
        if 'guardar_agregar_otro' in self.request.POST:
                return redirect('cursos:curso_crear')
        elif 'guardar_listar' in self.request.POST:
                return redirect('cursos:curso_listado')
        return result

    def form_invalid(self, form):
        messages.warning(self.request, f'{ICON_TRIANGLE} Por favor, corrija los errores a continuación.')
        # Imprimir los errores en la consola
        print("Errores del formulario:", form.errors)

        # Cambiar el template según el tipo de curso
        tipo_curso = self.request.GET.get('tipo', None)
        if tipo_curso == 'sec':
            self.template_name = 'curso/curso_alta_sec.html'
        elif tipo_curso == 'convenio':
            self.template_name = 'curso/curso_alta_convenio.html'
        elif tipo_curso == 'actividad':
            self.template_name = 'curso/curso_alta_gimnasio.html'
        else:
            self.template_name = 'curso/seleccion_tipo_curso.html'

        return super().form_invalid(form)
    
#--------------- CURSO DETALLE --------------------------------
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class CursoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Curso
    template_name = 'curso/curso_detalle.html'
    paginate_by = MAXIMO_PAGINATOR
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = self.object  # El objeto de curso obtenido de la vista

        context['titulo'] = f"{self.object.nombre}"
        context['tituloListado'] = 'Dictados Asociados'

        # Obtener todos los dictados asociados al curso junto con los horarios
        dictados = curso.dictado_set.prefetch_related('horarios').all()
        
        context['tiene_dictados'] = dictados.exists()
        context['filter_form'] = get_filtro_roles(self.request)

        # Configurar la paginación
        paginator = Paginator(dictados, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            dictados = paginator.page(page)
        except PageNotAnInteger:
            dictados = paginator.page(1)
        except EmptyPage:
            dictados = paginator.page(paginator.num_pages)

        context['dictados'] = dictados

        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
##--------------- CURSO LIST --------------------------------
class CursoListView(PermissionRequiredMixin, LoginRequiredMixin, ListFilterView):
    model = Curso
    paginate_by = MAXIMO_PAGINATOR
    filter_class = CursoFilterForm
    template_name = 'curso/curso_list.html'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aquí creas una instancia del formulario y la agregas al contexto
        filter_form = CursoFilterForm(self.request.GET)
        context['filtros'] = filter_form
        context['titulo'] = "Cursos"
        context['filter_form'] = get_filtro_roles(self.request)
        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Obtener los filtros del formulario
        filter_form = CursoFilterForm(self.request.GET)
        if filter_form.is_valid():
            nombre = filter_form.cleaned_data.get('nombre')
            areas = filter_form.cleaned_data.get('area')
            duracion = filter_form.cleaned_data.get('duracion')
            actividad = filter_form.cleaned_data.get('actividad')

            if nombre:
                queryset = queryset.filter(nombre__icontains=nombre)
            if areas:  # Si se seleccionaron áreas
                # Convertir el valor a una lista si no lo es
                if not isinstance(areas, list):
                    areas = [areas]
                # Filtrar por cada área seleccionada
                queryset = queryset.filter(area__in=areas)
            if duracion is not None:
                queryset = queryset.filter(duracion=duracion)
            if actividad:
                queryset = queryset.filter(actividad=actividad)

        queryset = queryset.order_by('nombre', 'area')
        return queryset

    def get_success_url(self):
        if self.request.POST['submit'] == "Guardar y Crear Dictado":
            return reverse_lazy('cursos:dictado_crear', args=[self.object.pk])
        return super().get_success_url()

##--------------- CURSO UPDATE --------------------------------

class CursoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Curso
    form_class = CursoForm
    success_url = reverse_lazy('cursos:curso')
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo_curso = self.get_object().get_tipo_curso()  # Obtén el tipo de curso
        context['tipo_curso'] = tipo_curso
        context['filter_form'] = get_filtro_roles(self.request)
        
        if tipo_curso == 'sec':
            context['titulo'] = "Modificar Curso del Sec"
        elif tipo_curso == 'convenio':
            context['titulo'] = "Modificar Convenio"
        elif tipo_curso == 'actividad':
            context['titulo'] = "Modificar Curso3"
        else:
            context['titulo'] = "Modificar Curso5"
        
        context['actividades'] = Actividad.objects.all().order_by('nombre')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tipo_curso = self.get_object().get_tipo_curso()  # Obtén el tipo de curso
        kwargs['initial'] = {'tipo_curso': tipo_curso}
        return kwargs

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        
        self.object = self.get_object()
        requiere_certificado_medico = self.object.requiere_certificado_medico
        
        if requiere_certificado_medico:
            self.template_name = 'curso/curso_alta_gimnasio.html'
        else:
            es_convenio = self.object.es_convenio
            if es_convenio:
                self.template_name = 'curso/curso_alta_convenio.html'
            else:
                self.template_name = 'curso/curso_alta_sec.html'
        return super().get(request, *args, **kwargs)
        
    def form_valid(self, form):
        curso = form.save()
        messages.success(self.request, f'{ICON_CHECK} Curso modificado con éxito')
        return redirect('cursos:curso_detalle', pk=curso.pk)

    def form_invalid(self, form):
        messages.warning(self.request, f'{ICON_TRIANGLE} Por favor, corrija los errores a continuación.')
        # Imprimir los errores en la consola
        print("Errores del formulario:", form.errors)
        tipo_curso = self.get_object().get_tipo_curso()  # Obtén el tipo de curso
        if tipo_curso == 'sec':
            self.template_name = 'curso/curso_alta_sec.html'
        elif tipo_curso == 'convenio':
            self.template_name = 'curso/curso_alta_convenio.html'
        elif tipo_curso == 'actividad':
            self.template_name = 'curso/curso_alta_gimnasio.html'
        else:
            self.template_name = 'curso/seleccion_tipo_curso.html'

        return super().form_invalid(form)



@permission_required('cursos.permission_gestion_curso', raise_exception=True)
@login_required(login_url='/login/')
def cursoListaEspera(request, pk):
    # Obtener el objeto Curso
    curso = Curso.objects.get(id=pk)
    dictados = Dictado.objects.filter(curso=curso, estado__lt=3).order_by('estado')

    dictados_con_cupo = []

    for dictado in dictados:
        # OBTENER A TODOS LOS ALUMNOS INSCRITOS (Afiliados, Familiares, Profesores)
        afiliado_inscritos = Afiliado.objects.filter(dictados=dictado)
        familiares_inscritos = Familiar.objects.filter(dictados=dictado)    
        profesores_inscritos = Profesor.objects.filter(dictados_inscriptos=dictado)
        alumnos_inscritos = Alumno.objects.filter(dictados=dictado)
        # CALCULAR EL TOTAL DE INSCRITOS
        total_inscritos = (
            afiliado_inscritos.count() +
            familiares_inscritos.count() +
            profesores_inscritos.count() +
            alumnos_inscritos.count()
        )
        # VERIFICAR SI EL DICTADO TIENE CUPO DISPONIBLE
        if total_inscritos < dictado.cupo_real:
            dictados_con_cupo.append(dictado)
    
    titulo = f'Inscritos en espera para {curso.nombre}'

    # OBTENER LA LISTA DE ESPERA ORDENADA POR TIPO Y FECHA DE INSCRIPCIÓN
    lista_espera = ListaEspera.objects.filter(curso=curso).order_by('rol__tipo', 'fechaInscripcion')

    context = {
        'curso': curso,
        'dictados': dictados_con_cupo,
        'titulo': titulo,
        'lista_espera': lista_espera,
        'curso_pk': pk,
    }
    return render(request, 'curso/curso_lista_espera.html', context)

##--------------- CURSO ELIMINAR --------------------------------

def dictadoFinalizado(dictado):
    return dictado.estado == 3

def todosDictadosFinalizados(curso):
    dictados = Dictado.objects.filter(curso=curso)
    return all(dictadoFinalizado(dictado) for dictado in dictados)





@permission_required('cursos.permission_gestion_curso', raise_exception=True)
@login_required(login_url='/login/')
def curso_eliminar(request, pk):
    curso = get_object_or_404(Curso, pk=pk)

    try:
        if todosDictadosFinalizados(curso):
            curso.fechaBaja = timezone.now()
            curso.save()
            mensaje_exito(request, f'El curso ha sido deshabilitado con exito')
        else:
            mensaje_error(request, f'No se puede eliminar el curso porque tiene dictados que no han finalizado')

    except Exception as e:
        messages.error(request, 'Ocurrió un error al intentar eliminar el aula.')
    return redirect('cursos:curso_detalle', pk=pk)

@permission_required('cursos.permission_gestion_curso', raise_exception=True)
@login_required(login_url='/login/')
def dictadosFinalizados(curso):
    dictados = Dictado.objects.all().filter(curso=curso)
    for dictado in dictados:
        if not dictado.estado == 3:
            return False
    return True

def obtenerTitularesVigente(profesores_titulares):
    for profesor in profesores_titulares:
        profesor = Profesor.objects.get(pk=profesor.pk)
        titulares = Titular.objects.filter(profesor=profesor)
    return True

from django.utils import timezone
from datetime import datetime, timedelta

from django.db.models import Q

def obtenerProfesoresActivos():
    roles_sin_fecha_hasta = Rol.objects.filter(hasta__isnull=True)
     # Obtener personas asociadas a los roles sin fecha de finalización
    personas = Persona.objects.filter(roles__in=roles_sin_fecha_hasta)
    # Obtener profesor asociados a las personas obtenidas
    return Profesor.objects.filter(persona__in=personas)

def obtenerUltimoDiaMesAnterior():
    hoy = timezone.now()
    primer_dia_mes_actual = hoy.replace(day=1)
    return primer_dia_mes_actual - timedelta(days=1)

def obtenerProfesoresConDictados(titulares_ya_finalizados, titulares_vigentes):
    # Obtener profesores asociados a titulares con dictados finalizados el mes pasado
    profesores_finalizados = Profesor.objects.filter(titular__in=titulares_ya_finalizados).distinct()
    
    # Obtener profesores asociados a titulares con dictados vigentes
    profesores_vigentes = Profesor.objects.filter(titular__in=titulares_vigentes).distinct()
    
    # Combinar los profesores de ambos grupos
    profesores = profesores_finalizados | profesores_vigentes
    
    return profesores

import json

def obtenerTitularesConClasesEnMesPasado():
    titulares_con_clases = []

    ultimo_dia_mes_anterior = obtenerUltimoDiaMesAnterior()
    primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)

    for titular in Titular.objects.all():
        dictado = titular.dictado
        clases = Clase.objects.filter(
            reserva__horario__dictado=dictado,
            reserva__fecha__range=(primer_dia_mes_anterior, ultimo_dia_mes_anterior)
        )
        if clases.exists():
            titulares_con_clases.append(titular)

    return titulares_con_clases

def obtenerProfesoresUnicos(titulares):
    profesores_unicos = set()
    for titular in titulares:
        profesores_unicos.add(titular.profesor)
    return profesores_unicos

class PagoProfesorCreateView(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    model = PagoProfesor
    form_class = PagoProfesorForm
    template_name = 'pago/pago_profesor.html'
    success_url = reverse_lazy('cursos:pago_profesor')
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        titulares_con_clases_mes_pasado = obtenerTitularesConClasesEnMesPasado()
        profesores_unicos = obtenerProfesoresUnicos(titulares_con_clases_mes_pasado)
        context['profesores'] = profesores_unicos
        context['titulo'] = "Comprobante de pago del profesor"
        context['filter_form'] = get_filtro_roles(self.request)
        return context

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        enc_profesor = self.request.POST.get('profesor')
        total_a_pagar = self.request.POST.get('total_a_pagar')
        datos_dictados = self.request.POST.get('datos_dictados')

        if enc_profesor == '0':
            mensaje_advertencia(self.request, f'Seleccione al profesor')
            return super().form_invalid(form)
        
        if datos_dictados:
            dictados_info = json.loads(datos_dictados)
            pago = form.save(commit=False)
            pago.profesor_id = enc_profesor
            pago.total = total_a_pagar
            pago.save()

            for dictado_info in dictados_info:
                pk = dictado_info.get('pk')
                dictado = get_object_or_404(Dictado, pk=pk)

               # Crear una instancia de DetallePagoProfesor para cada dictado asociado al pago
                DetallePagoProfesor.objects.create(
                    pago_profesor=pago,
                    dictado=dictado,
                    total_clases=dictado_info.get('total_clases'),
                    clases_asistidas=dictado_info.get('clases_asistidas'),
                    porcentaje_asistencia=dictado_info.get('porcentaje_asistencia'),
                    precioFinal=dictado_info.get('precioFinal'),
                )
            pago.generarPreFactura()

        mensaje_exito(self.request, f'{MSJ_CORRECTO_PAGO_REALIZADO}')
        self.object = form.save()

        if 'guardar_y_recargar' in self.request.POST:
            return self.render_to_response(self.get_context_data(form=self.form_class()))   
        elif 'guardar_y_listar' in self.request.POST:
            return redirect('cursos:pago_cuota_profesor_listado')
        return super().form_valid(form)

    def form_invalid(self, form):
        mensaje_advertencia(self.request, MSJ_CORRECTION)
        print("")
        print("ERRORES DEL FORMULARIO")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error en el campo '{field}': {error}")
        print("")
        return super().form_invalid(form)
    
class PagoProfesorListView(LoginRequiredMixin, PermissionRequiredMixin, ListFilterView):
    model = PagoProfesor
    filter_class = PagoProfesorFilterForm
    template_name = 'pago/pago_profesor_listado.html'
    paginate_by = MAXIMO_PAGINATOR
    success_url = reverse_lazy('afiliados:pago_cuota_listado')
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Pago de profesor"
        context['filter_form'] = get_filtro_roles(self.request)
        return context

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = PagoProfesorFilterForm(self.request.GET)
        if form.is_valid():
            persona_dni = form.cleaned_data.get('profesor__persona__dni')
            curso = form.cleaned_data.get('curso')
        return queryset

from django.http import HttpResponse
class PagoProfesorDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = PagoProfesor
    template_name = 'pago/pago_profesor_detalle.html'
    paginate_by = MAXIMO_PAGINATOR
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pago = self.object  # El objeto de curso obtenido de la vista

        context['titulo'] = "Detalle del pago"
        context['tituloListado'] = "Clases pagadas"
        context['pago'] = pago
        
        return context

    def render_to_response(self, context, **response_kwargs):
        # Si se solicita un PDF, generamos y devolvemos el PDF
        if 'pdf' in self.request.GET:
            pago = context['pago']
            pdf = pago.generarPdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Comprobante-pre-factura.pdf"'
            return response
        else:
            # De lo contrario, renderizamos la plantilla normalmente
            return super().render_to_response(context, **response_kwargs)

def getObjectRolTipo(rol):

    if rol.tipo == 1: 
        return get_object_or_404(Afiliado, persona__pk=rol.persona.pk), False
    elif rol.tipo == 2:
        return get_object_or_404(Familiar, persona__pk=rol.persona.pk), False
    elif rol.tipo == 3:
        return get_object_or_404(Alumno, persona__pk=rol.persona.pk), False
    elif rol.tipo == 4: 
        return get_object_or_404(Profesor, persona__pk=rol.persona.pk), True
    elif rol.tipo == 5:
        return get_object_or_404(Encargado, persona__pk=rol.persona.pk), False

def obtenerDictados(persona, es_profesor):
    
    if es_profesor:
        return persona.dictados_inscriptos.all()
    else:
        return persona.dictados.all()

def estaEnDictadoActivo(persona, es_profesor):

    dictados = obtenerDictados(persona, es_profesor)

    if dictados.exists():
        for dictado in dictados:
            print("dictado", dictado)
            if dictado.estado == 2:
                print("ESTA ACTIVO")
                return True
    return False

def obtenerAlumnosEnDictadoActivo():
    #Obtengo todos los roles activos
    roles_sin_fecha_hasta = Rol.objects.filter(hasta__isnull=True)
    resultados = []

    for rol in roles_sin_fecha_hasta:
        persona, es_profesor = getObjectRolTipo(rol)
        
        if estaEnDictadoActivo(persona, es_profesor):
            resultados.append({"alumnos": persona})
    return resultados

def tienenCantidadApropiada(dictados_info):
    for dictado_info in dictados_info:
        pagos_faltantes = dictado_info.get('aux')
        cantidad = dictado_info.get('cantidad')
        if cantidad > pagos_faltantes:
            return False

    return True


class PagoAlumnoCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = PagoAlumno
    form_class = PagoRolForm
    template_name = 'pago/pago_alumno.html'
    success_url = reverse_lazy('cursos:pago_profesor')
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alumnos = obtenerAlumnosEnDictadoActivo()
        context['titulo'] = "Comprobante de pago del alumno"
        context['alumnos'] = alumnos
        context['filter_form'] = get_filtro_roles(self.request)
        return context

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        pk = self.request.POST.get('alumno')
        
        if pk == '0':
            mensaje_advertencia(self.request, f'Seleccione al alumno')
            return super().form_invalid(form)

        rol = get_object_or_404(Rol, pk=pk)
        datos_dictados = self.request.POST.get('dictados_seleccionados')
        total_a_pagar = self.request.POST.get('total_a_pagar')

        if datos_dictados:
            dictados_info = json.loads(datos_dictados)

            if not tienenCantidadApropiada(dictados_info):
                mensaje_error(self.request, f'Ocurrio un error porque la cantidad supera los pagos faltantes')
                return redirect('cursos:pago_alumno_crear')

            pago = form.save(commit=False)
            pago.rol_id = pk
            pago.total = total_a_pagar
            pago.save()

            for dictado_info in dictados_info:
                dictado_pk = dictado_info.get('valor')
                dictado = get_object_or_404(Dictado, pk=dictado_pk)
                precioConDescuento = round(float(dictado_info.get('precioConDescuento')), 2)
                cantidad = int(dictado_info.get('cantidad'))
                total = precioConDescuento * cantidad

               # Crear una instancia de DetallePagoAlumno para cada dictado asociado al pago
                DetallePagoAlumno.objects.create(
                    pago_alumno=pago,
                    dictado=dictado,
                    cantidad = cantidad,
                    precioFinal = dictado_info.get('precio'),
                    descuento = dictado_info.get('descuento'),
                    periodo_pago = dictado.periodo_pago,
                    precioConDescuento = precioConDescuento,
                    total = total,
                )

            pago.generarPreFactura()
            mensaje_exito(self.request, f'{MSJ_CORRECTO_PAGO_REALIZADO}')
            self.object = form.save()

            if 'guardar_y_recargar' in self.request.POST:
                return self.render_to_response(self.get_context_data(form=self.form_class()))   
            elif 'guardar_y_listar' in self.request.POST:
                return redirect('cursos:pago_cuota_alumno_listado')
            return super().form_valid(form)
    
    def form_invalid(self, form):
        mensaje_advertencia(self.request, MSJ_CORRECTION)
        print("")
        print("ERRORES DEL FORMULARIO")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error en el campo '{field}': {error}")
        print("")
        return super().form_invalid(form)
    

class PagoAlumnoListView(LoginRequiredMixin,PermissionRequiredMixin,ListFilterView):
    model = PagoAlumno
    filter_class = PagoAlumnoFilterForm
    template_name = 'pago/pago_alumno_listado.html'
    paginate_by = MAXIMO_PAGINATOR
    success_url = reverse_lazy('afiliados:pago_cuota_listado')
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Pago de alumnos"
        context['filter_form'] = get_filtro_roles(self.request)
        return context

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
    
    # def get_queryset(self):
    #     print("-------1----")
    #     queryset = super().get_queryset()
    #     form = PagoAlumnoFilterForm(self.request.GET)
    #         rol = form.cleaned_data.get('rol')
    #         if rol:
    #             queryset = queryset.filter(rol=rol)
            
    #         curso = form.cleaned_data.get('curso')
    #     return queryset
    
    def render_to_response(self, context, **response_kwargs):
        # Si se solicita un PDF, generamos y devolvemos el PDF
        if 'pdf' in self.request.GET:
            pago = context['pago']
            pdf = pago.generarPdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Comprobante-pre-factura.pdf"'
            return response
        else:
            # De lo contrario, renderizamos la plantilla normalmente
            return super().render_to_response(context, **response_kwargs)

class PagoAlumnoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = PagoAlumno
    template_name = 'pago/pago_profesor_detalle.html'
    paginate_by = MAXIMO_PAGINATOR
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pago = self.object  # El objeto de curso obtenido de la vista

        context['titulo'] = "Detalle del pago"
        context['tituloListado'] = "Clases pagadas"
        context['pago'] = pago
        
        return context

    def render_to_response(self, context, **response_kwargs):
        # Si se solicita un PDF, generamos y devolvemos el PDF
        if 'pdf' in self.request.GET:
            pago = context['pago']
            pdf = pago.generarPdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Comprobante-pre-factura.pdf"'
            return response
        else:
            # De lo contrario, renderizamos la plantilla normalmente
            return super().render_to_response(context, **response_kwargs)

