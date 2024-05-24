from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView, ListView

from apps.afiliados.views import redireccionar_detalle_rol
from sec2.utils import get_filtro_roles, get_selected_rol_pk
from utils.funciones import mensaje_advertencia, mensaje_error, mensaje_exito
from ..models import Aula, Clase, Dictado, Horario, Reserva
from ..forms.aula_forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required , login_required
from datetime import date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

## ------------  CREATE AND LIST AULA -------------------
class GestionAulaView(PermissionRequiredMixin, LoginRequiredMixin, CreateView, ListView):
    model = Aula
    template_name = 'aula/gestion_aula.html'  
    form_class = AulaForm
    paginate_by = MAXIMO_PAGINATOR
    context_object_name = 'aulas'
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Gestión de Aula"
        context['form'] = self.get_form()
        context['aulas'] = self.get_queryset()  # Use filtered queryset
        context['filtros'] = AulaFilterForm()
        context['filter_form'] = get_filtro_roles(self.request)

        return context

    def get_success_url(self):
        return reverse_lazy('cursos:gestion_aula')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        mensaje_exito(self.request, f'{MSJ_AULA_ALTA_EXITOSA}')
        return response
    
    def form_invalid(self, form):
        mensaje_advertencia(self.request, f'{MSJ_TIPO_NUMERO_EXISTE}')
        return redirect('cursos:gestion_aula')
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        # Asegúrate de que el queryset esté disponible antes de llamar a super().get()
        self.object_list = self.get_queryset()
        return super(CreateView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Aula.objects.all()
        # Obtener los filtros del formulario
        filter_form = AulaFilterForm(self.request.GET)
        
        if filter_form.is_valid():
            capacidad = filter_form.cleaned_data.get('capacidad')
            tipo = filter_form.cleaned_data.get('tipo')
            # Aplicar filtros según sea necesario
            if capacidad:
                queryset = queryset.filter(capacidad__gte=capacidad)  # Ajuste aquí
            if tipo:
                queryset = queryset.filter(tipo=tipo)
        # Ordenar de forma descendente por tipo y luego por número
        queryset = queryset.order_by('-tipo', 'numero')
        return queryset

## ------------ ACTIVIDAD DETALLE -------------------

class AulaDetailView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    model = Aula
    template_name = "aula/aula_detalle.html"
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'
    paginate_by = MAXIMO_PAGINATOR


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aula = self.object
        current_date = date.today()  # Get the current date
        
        reservas = Reserva.objects.filter(aula=aula, fecha__gte=current_date).order_by('fecha', 'horario__hora_inicio')
        
        # Configurar la paginación
        paginator = Paginator(reservas, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            reservas = paginator.page(page)
        except PageNotAnInteger:
            reservas = paginator.page(1)
        except EmptyPage:
            reservas = paginator.page(paginator.num_pages)

        context['reservas'] = reservas

        context['titulo'] = 'Detalle de Aula'
        context['tituloListado'] = 'Proximas reservas del aula'
        context['filter_form'] = get_filtro_roles(self.request)

        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
## ------------ UPDATE -------------------
class AulaUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Aula
    form_class = AulaForm
    template_name = 'aula/aula_alta.html'
    context_object_name = 'aula'
    success_url = reverse_lazy('cursos:gestion_actividad')
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Modificar Aula"
        context['filtros'] = AulaFilterForm()
        context['filter_form'] = get_filtro_roles(self.request)
        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        if rol is not None:
            return redireccionar_detalle_rol(rol)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        aula = form.save()
        messages.success(self.request, f'{ICON_CHECK} Aula modificado con éxito')
        return redirect('cursos:aula_detalle', pk=aula.pk)

    def form_invalid(self, form):
        messages.warning(self.request, f'{ICON_TRIANGLE} Atencion:')
        for field, errors in form.errors.items():
            print(f"Campo: {field}, Errores: {', '.join(errors)}")
        return super().form_invalid(form)


def obtenerDictadosAsociados(aula):
    # Obtener las reservas relacionadas con el aula específica
    reservas = Reserva.objects.filter(aula=aula)
    horarios = Horario.objects.filter(reservass__in=reservas)
    # Obtener los dictados distintos asociados a los horarios
    dictados_distintos = horarios.values('dictado').distinct()
    dictados = Dictado.objects.filter(id__in=dictados_distintos)
    return dictados

def existenDictadosVigentes(dictados):
    return any(dictado.estado in [1, 2] for dictado in dictados)

## ------------ ELIMINAR -------------------
def aula_eliminar(request, pk):
    # Se va a eliminar siempre cuando no existan dictados vigentes con reserva en el aula
    aula = get_object_or_404(Aula, pk=pk)
    dictados = obtenerDictadosAsociados(aula)
    try:
        if existenDictadosVigentes(dictados):
            mensaje_error(request, "El aula tiene futuras reservas para dictados.")
            return redirect('cursos:gestion_aula')
        aula.delete()
        mensaje_exito(request, "El aula se eliminó correctamente!")
    except Exception as e:
            mensaje_error(request, "Ocurrió un error al intentar eliminar el aula.")
    return redirect('cursos:gestion_aula')