from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView

from apps.afiliados.views import redireccionar_detalle_rol
from apps.cursos.views.aula_views import existenDictadosVigentes
from sec2.utils import get_filtro_roles, get_selected_rol_pk
from utils.funciones import mensaje_advertencia, mensaje_error, mensaje_exito
from ..models import Actividad, Curso, Dictado
from ..forms.actividad_forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.detail import DetailView

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required , login_required 
from django.utils.text import capfirst


## ------------  CREATE AND LIST ACTIVIDAD -------------------

class GestionActividadView(LoginRequiredMixin, PermissionRequiredMixin, CreateView, ListView):
    model = Actividad
    template_name = 'actividad/gestion_actividad.html'
    form_class = ActividadForm
    paginate_by = MAXIMO_PAGINATOR
    context_object_name = 'actividades'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Gestión de Actividad"
        context['form'] = self.get_form()
        context['filtros'] = ActividadFilterForm()
        context['filter_form'] = get_filtro_roles(self.request)
        return context



    def get_success_url(self):
        return reverse_lazy('cursos:gestion_actividad')

    def form_valid(self, form):
        nombre = form.cleaned_data['nombre']
        # Convierte el nombre a título (primera letra en mayúscula, resto en minúscula)
        nombre_formateado = capfirst(nombre.lower())
        form.instance.nombre = nombre_formateado
        mensaje_exito(self.request, f'{MSJ_ACTIVIDAD_ALTA_EXITOSA}')
        return super().form_valid(form)

    def form_invalid(self, form):
        mensaje_advertencia(self.request, f'{MSJ_NOMBRE_EXISTE}')
        return redirect('cursos:gestion_actividad')

    def get_queryset(self):
        queryset = super().get_queryset()

        filter_form = ActividadFilterForm(self.request.GET)
        if filter_form.is_valid():
            nombre_filter = filter_form.cleaned_data.get('nombre')
            if nombre_filter:
                queryset = queryset.filter(nombre__icontains=nombre_filter)

        return queryset.order_by('nombre')

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        self.object_list = self.get_queryset()
        
        return super().get(request, *args, **kwargs)

## ------------ ACTIVIDAD DETALLE -------------------
class ActividadDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Actividad
    template_name = 'actividad/actividad_detalle.html'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actividad = self.object  # Access the Afiliado instance

        cursos = Curso.objects.all().filter(actividad=actividad)
        context['titulo'] = 'Detalle de Actividad'
        context['tituloListado'] = 'Cursos con actividad'
        context['cursos'] = cursos
        context['filter_form'] = get_filtro_roles(self.request)

        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
## ------------ ACTIVIDAD UPDATE -------------------
class ActividadUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Actividad
    form_class = ActividadForm
    template_name = 'actividad/actividad_alta.html'
    success_url = reverse_lazy('cursos:gestion_actividad')
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Modificar Actividad"
        context['filtcer_form'] = get_filtro_roles(self.request)
        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        actividad = form.save()
        mensaje_exito(self.request, f'{MSJ_EXITO_MODIFICACION}')
        return redirect('cursos:actividad_detalle', pk=actividad.pk)

    def form_invalid(self, form):
        mensaje_advertencia(self.request, f'{MSJ_NOMBRE_EXISTE}')
        for field, errors in form.errors.items():
            print(f"Campo: {field}, Errores: {', '.join(errors)}")
        return super().form_invalid(form)


def obtenerCursosAsociados(actividad):
    return Curso.objects.all().filter(actividad=actividad)

# ## ------------ ACTIVIDAD DELETE -------------------
    
@permission_required('cursos.permission_gestion_curso', raise_exception=True)
@login_required(login_url='/login/')
def actividad_eliminar(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    cursos = obtenerCursosAsociados(actividad)
    dictados = Dictado.objects.filter(curso__in=cursos)
    dictados = Dictado.objects.filter(id__in=dictados)

    try:
        if existenDictadosVigentes(dictados):
            mensaje_error(request, "La actividad tiene cursos que tienen dictados vigentes.")
            return redirect('cursos:gestion_actividad')
        actividad.delete()
        mensaje_exito(request, f'{MSJ_ACTIVIDAD_EXITO_BAJA}')
    except Exception as e:
        mensaje_error(request, f'{MSJ_ERROR_ELIMINAR}')
    return redirect('cursos:gestion_actividad')