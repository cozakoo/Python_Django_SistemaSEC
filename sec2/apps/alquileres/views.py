from django.shortcuts import get_object_or_404, render
from apps.afiliados.views import existe_persona_activa, redireccionar_detalle_rol
from apps.alquileres.forms import *
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import datetime
from django.views.generic import DetailView, ListView,TemplateView
from apps.personas.models import Rol

from utils.funciones import mensaje_advertencia, mensaje_error, mensaje_exito  
from .models import Alquiler, Salon, Servicio, Encargado, Afiliado, Pago_alquiler
from .forms import *
from sec2.utils import ListFilterView, get_filtro_roles, get_selected_rol_pk
from django.db import transaction  # Agrega esta línea para importar el módulo transaction
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
#CONSTANTE
from utils.constants import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required , login_required

# Create your views here.
# ----------------------------- ALQUILER VIEW ----------------------------------- #
def index(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

# ----------------------------- CREATE DE ENCARGADO  ----------------------------------- #
class EncargadoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Persona
    form_class = EncargadorForm
    template_name = 'encargado_form.html'
    success_url = reverse_lazy('alquiler:encargado_listar')
    title = "Alta de encargado"
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.title  # Agrega el título al contexto
        context['filter_form'] = get_filtro_roles(self.request)
        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        dni = form.cleaned_data["dni"]
        if existe_persona_activa(self, dni):
            mensaje_error(self.request, f'{MSJ_PERSONA_EXISTE}')
            form = EncargadorForm(self.request.POST)
            return self.render_to_response(self.get_context_data(form=form))
        else:
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
                es_encargado = True
            )
            persona.save()

            current_datetime = timezone.now()

            encargado = Encargado(
                persona=persona,
                tipo = Encargado.TIPO,
                desde = current_datetime,
            )
            encargado.save()
            if 'guardar_y_recargar' in self.request.POST:
                mensaje_exito(self.request, f'{MSJ_CORRECTO_ALTA_AFILIADO}')
                self.object = form.save()
                return self.render_to_response(self.get_context_data(form=self.form_class()))   

            elif 'guardar_y_listar' in self.request.POST:
                # Guarda el objeto y redirige a la página de listar
                self.object = form.save()    
                return redirect('alquiler:encargado_listar')
        
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, '<i class="fa-solid fa-triangle-exclamation fa-flip"></i> Por favor, corrija los errores a continuación.')
        return super().form_invalid(form)

from django.db.models import Q

# ----------------------------- LISTADO DE ENCARGADO  ----------------------------------- #
class EncargadoListView(LoginRequiredMixin, PermissionRequiredMixin, ListFilterView):
    model = Encargado
    filter_class = EncargadoFilterForm
    template_name = 'encargado_listar.html'
    paginate_by = MAXIMO_PAGINATOR
    success_url = reverse_lazy('alquiler:encargado_listar')
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Encargados"
        context['filter_form'] = get_filtro_roles(self.request)
        return context
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = EncargadoFilterForm(self.request.GET)
        if form.is_valid():
            persona_dni = form.cleaned_data.get('persona__dni')
            persona_apellido = form.cleaned_data.get('persona__apellido')

            if persona_dni:
                queryset = queryset.filter(persona__dni=persona_dni)
            if persona_apellido:
                queryset = queryset.filter(persona__apellido=persona_apellido)
        return queryset

    def get_success_url(self):
        if self.request.POST['submit'] == "Guardar y Crear Encargado":
            return reverse_lazy('alquiler:encargado_alta', args=[self.object.pk])
        return super().get_success_url()



# ----------------------------- CREATE DE SERVICIO  ----------------------------------- #
class servicioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Servicio
    form_class = ServiciorForm
    template_name = 'Servicio_form.html'
    success_url = reverse_lazy('alquiler:Servicio_form')
    title = "Formulario Alta de Servicio"  # Agrega un título
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'
  


class EncargadoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Encargado
    template_name = 'encargado_detalle.html'
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo'] = "Detalle del Encargado"
        context['tituloListado1'] = "Salones a cargo"
        context['filter_form'] = get_filtro_roles(self.request)
        return context
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
    
class EncargadoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Encargado
    form_class = EncargadoUpdateForm
    template_name = 'encargado_form.html'  
    success_url = reverse_lazy('cursos:profesor_listado')
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True
        context['titulo'] = "Modificar Encargado"
        context['filter_form'] = get_filtro_roles(self.request)
        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        mensaje_exito(self.request, f'{MSJ_EXITO_MODIFICACION}')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form.errors)
        return super().form_invalid(form)

# ----------------------------- CREATE DE SERVICIO  ----------------------------------- #
class GestionServicioView(PermissionRequiredMixin, LoginRequiredMixin, CreateView, ListView):
    model = Servicio
    template_name = 'gestion_servicio.html'  
    form_class = ServiciorForm
    paginate_by = MAXIMO_PAGINATOR
    context_object_name = 'servicios'
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Gestión de Servicio"
        context['form'] = self.get_form()
        context['filtros'] = ServicioFilterForm()
        context['filter_form'] = get_filtro_roles(self.request)
        return context

    def get_success_url(self):
        return reverse_lazy('alquiler:gestion_servicio')
    
    def form_valid(self, form):
        form.instance.nombre = form.cleaned_data['nombre'].title()
        mensaje_exito(self.request, f'{MSJ_SERVICIO_ALTA_EXITOSA}')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        mensaje_advertencia(self.request, f'{MSJ_TIPO_NUMERO_EXISTE}')
        return redirect('cursos:gestion_servicio')
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)
        
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Obtener los filtros del formulario
        filter_form = ServicioFilterForm(self.request.GET)
        if filter_form.is_valid():
            nombre_filter = filter_form.cleaned_data.get('nombre')
            if nombre_filter:
                queryset = queryset.filter(nombre__icontains=nombre_filter)
        return queryset.order_by('nombre')



class ServicioDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Servicio
    template_name = "servicio_detalle.html"
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detalle de Servicio'
        return context
    

class ServicioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Servicio
    form_class = ServiciorForm
    template_name = 'Servicio_form.html'
    success_url = reverse_lazy('alquiler:gestion_servicio')
    title = "Formulario Alta de Servicio"  # Agrega un título
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.title
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'{ICON_CHECK} Alta de servicio exitosa!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, '<i class="fa-solid fa-triangle-exclamation fa-flip"></i> Por favor, corrija los errores a continuación.')
        return super().form_invalid(form)
    
class ServicioUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Servicio
    form_class = ServiciorForm
    template_name = 'Servicio_form.html'
    success_url = reverse_lazy('alquiler:gestion_servicio')
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Modificar Servicio"
        return context

    def form_valid(self, form):
        actividad = form.save()
        mensaje_exito(self.request, f'{MSJ_EXITO_MODIFICACION}')
        return redirect('alquiler:gestion_servicio')

    def form_invalid(self, form):
        mensaje_advertencia(self.request, f'{MSJ_NOMBRE_EXISTE}')
        for field, errors in form.errors.items():
            print(f"Campo: {field}, Errores: {', '.join(errors)}")
        return super().form_invalid(form)

# ----------------------------- LISTADO DE SERVICIO  ----------------------------------- #
class ServiciosListView(PermissionRequiredMixin,LoginRequiredMixin,ListFilterView):
    model = Servicio
    paginate_by = 100
    filter_class = ServicioFilterForm
    success_url = reverse_lazy('alquiler:servicio_listar')
    template_name = 'servicio_listar.html'
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Listado de Servicios"
        return context

    def get_success_url(self):
        if self.request.POST['submit'] == "Guardar y Crear Servicio":
            return reverse_lazy('alquiler:servicio_crear', args=[self.object.pk])
        return super().get_success_url()            

# ## ------------ ACTIVIDAD DELETE -------------------
def servicio_eliminar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    salones = Salon.objects.filter(servicios=servicio)
    if salones.exists():
        mensaje_error(request, f'No puede ser eliminado porque está siendo utilizado por al menos un salón.')
        return redirect('alquiler:gestion_servicio')
    try:
        # Realiza aquí cualquier acción necesaria antes de eliminar el servicio
        servicio.delete()
        mensaje_exito(request, f'El servicio ha sido eliminado exitosamente.')
    except Exception as e:
        mensaje_error(request, f'Ocurrió un error al intentar eliminar la el servicio.')
    return redirect('alquiler:gestion_servicio')

# ----------------------------- CREATE DE SALON  ----------------------------------- #
class SalonCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Salon
    form_class = SalonrForm
    template_name = 'salon_form.html'
    success_url = reverse_lazy('alquiler:salon_crear')
    title = "Formulario de Salon"
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.title
        context['servicios'] = Servicio.objects.all()
        context['filter_form'] = get_filtro_roles(self.request)
        return context

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        if 'guardar_y_recargar' in self.request.POST:
                mensaje_exito(self.request, f'Alta de salón exitoso')
                self.object = form.save()
                return self.render_to_response(self.get_context_data(form=self.form_class()))   

        elif 'guardar_y_listar' in self.request.POST:
                # Guarda el objeto y redirige a la página de listar
                mensaje_exito(self.request, f'Alta de salón exitoso')
                self.object = form.save()    
                return redirect('alquiler:salon_listar')
        
        mensaje_exito(self.request, f'{MSJ_CORRECTO_ALTA_SALON}')
        return redirect('alquiler:salon_listar')

    def form_invalid(self, form):
        mensaje_advertencia(self.request, f'{MSJ_CORRECTION}')
        return super().form_invalid(form)

# ----------------------------- DETAIL DE SALON  ----------------------------------- #
class SalonDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Salon
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'
    template_name = 'salon_detalle.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f"{self.object.nombre}"
        context['tituloListado1'] = "Alquileres a cargo"

        return context
    
# ----------------------------- LIST DE SALON  ----------------------------------- #
class SalonesListView(LoginRequiredMixin, PermissionRequiredMixin, ListFilterView):
    model = Salon
    filter_class = SalonFilterForm
    template_name = 'salon_list.html'
    paginate_by = MAXIMO_PAGINATOR
    success_url = reverse_lazy('alquiler:salon_listar')
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Salones"
        context['filter_form'] = get_filtro_roles(self.request)
        return context

    def get_success_url(self):
        if self.request.POST['submit'] == "Guardar y Crear Salon":
            return reverse_lazy('alquiler:salon_crear', args=[self.object.pk])
        return super().get_success_url()        

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Obtén los parámetros de filtro del formulario
        nombre = self.request.GET.get('nombre')
        localidad = self.request.GET.get('localidad')
        capacidad = self.request.GET.get('capacidad')

        # Filtrar los salones según los parámetros ingresados
        if capacidad:
            capacidad = int(capacidad)  # Convertir la capacidad a entero
            queryset = queryset.filter(capacidad__gte=capacidad)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        if localidad:
            queryset = queryset.filter(localidad=localidad)

        return queryset.order_by('nombre')

# ----------------------------- UPDATE DE SALON  ----------------------------------- #

class SalonUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Salon
   # form_class = AlquilerForm
    template_name = 'alquiler/salon_form.html'
    success_url = reverse_lazy('alquiler:salon')
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Modificar salon"
        return context
    
    def form_valid(self, form):
     
        messages.success(self.request, '<i class="fa-solid fa-square-check fa-beat-fade"></i> salon modificado con éxito')
        return redirect('alquiler:salon_detalle')

    def form_invalid(self, form):
        messages.warning(self.request, '<i class="fa-solid fa-triangle-exclamation fa-flip"></i> Por favor, corrija los errores a continuación.')
        for field, errors in form.errors.items():
            print(f"Campo: {field}, Errores: {', '.join(errors)}")
        return super().form_invalid(form) 
    



def salon_eliminar(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    alquileres = Alquiler.objects.filter(salon=salon)

    if alquileres.exists():
        mensaje_error(request, f'No puede ser eliminado porque tiene alquileres asociados.')
        return redirect('alquiler:salon_detalle', pk=salon.pk)
    try:
        salon.fechaBaja = timezone.now()
        salon.save()
        mensaje_exito(request, f'El salon ha sido dado de baja con exito')
    except Exception as e:
        messages.error(request, 'Ocurrió un error al intentar eliminar el aula.')
    return redirect('alquiler:salon_detalle', pk=salon.pk)

# ----------------------------- CREATE DE ALQUILER  ----------------------------------- #

class AlquilerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Alquiler
    form_class = AlquilerForm
    template_name = 'alquiler_form.html'
    success_url = reverse_lazy('alquiler:pagar_alquiler_crear')
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'
    title = "Alquiler de Salón" 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.title  # Agrega el título al contexto
        return context

    def form_valid(self, form):
        salon = form.cleaned_data["salon"]
        fecha = form.cleaned_data["fecha_alquiler"]
        turno = form.cleaned_data["turno"]
        print("salon", salon)
        print("fecha", fecha)
        print("turno", turno)
        alquiler = Alquiler.objects.first()
        if Alquiler.fecha_valida(fecha):
            if alquiler is not None:
                if alquiler.verificar_existencia_alquiler(salon, fecha, turno):
                    #el alquiler ya existe
                    messages.error(self.request, f'{ICON_ERROR} Ya existía un alquiler del salón {salon} en la fecha {fecha} en el turno {turno}.')
                    return self.render_to_response(self.get_context_data(form=form))
                else:
                    #el alquiler no exite y se puede alquilar. Guardar el nuevo alquiler
                    messages.success(self.request, f'{ICON_CHECK} Alquiler exitosa!')
                    return super().form_valid(form)
            else: 
                # es el primer alquiler y se guarda
                messages.success(self.request, f'{ICON_CHECK} Alquiler creado con éxito!')
                return super().form_valid(form)
        else:
             messages.error(self.request, f'{ICON_ERROR} La fecha {fecha.strftime("%d-%m-%Y")} es anterior a la fecha de hoy.')
             return self.render_to_response(self.get_context_data(form=form))
       
        
            
    def form_invalid(self, form):
        messages.warning(self.request, '<i class="fa-solid fa-triangle-exclamation fa-flip"></i> Por favor, corrija los errores a continuación.')
        return super().form_invalid(form)
    
    def fecha_valida(fecha):
        """Verifica que la fecha sea mayor a la de hoy"""
        hoy = datetime.today()
        try:
            fecha_formateada = datetime.strptime(fecha, '%Y-%m-%d').date()
            if fecha_formateada >= hoy.date():
                return True
            else:
                raise ValueError('La fecha debe ser superior a la actual')
        except ValueError as e:
            raise forms.ValidationError(e)
            
   
def agregar_lista_espera(request, pk):
    alquiler = get_object_or_404(Alquiler, pk=pk)
    
    afiliado_inquilino = alquiler.afiliado

    roles_sin_fecha_hasta = Rol.objects.filter(hasta__isnull=True, tipo=1)
    # Obtener personas asociadas a los roles sin fecha de finalización
    personas = Persona.objects.filter(roles__in=roles_sin_fecha_hasta)
    # Obtener afiliados asociados a las personas obtenidas
    afiliados = Afiliado.objects.filter(persona__in=personas, estado=2).exclude(pk=afiliado_inquilino.pk)  # Excluir el afiliado inquilino
    afiliado_en_lista_espera = alquiler.lista_espera.all()
    afiliados_no_en_lista_espera = afiliados.exclude(pk__in=afiliado_en_lista_espera.values_list('pk', flat=True))

    if request.method == 'POST':
        enc_afiliado_id = request.POST.get('enc_afiliado')
        print("ENC AFILIADO", enc_afiliado_id)
        if enc_afiliado_id and enc_afiliado_id != '0':
            afiliado = get_object_or_404(Afiliado, pk=enc_afiliado_id)
            alquiler.lista_espera.add(afiliado)
            alquiler.save()
            mensaje_exito(request, 'Agregado a la lista de espera con exito')

    context = {
        'alquiler': alquiler,
        'afiliados': afiliados_no_en_lista_espera,
    }
    
    return render(request, 'lista_espera_alquiler.html', context)

# ----------------------------- LIST DE ALQUILER  ----------------------------------- #

from .forms import PagoForm
from django.shortcuts import redirect

def reemplazar_inquilino(request, pk):
    alquiler = get_object_or_404(Alquiler, pk=pk)
    lista_espera = alquiler.lista_espera

    if request.method == 'POST':
        nuevo_afiliado_pk = request.POST.get('enc_afiliado')
        if nuevo_afiliado_pk:  
            nuevo_afiliado = get_object_or_404(Afiliado, pk=nuevo_afiliado_pk)
            actualizar_alquiler_y_pago(alquiler, nuevo_afiliado, request.POST)

            detalle_alquiler_url = reverse('alquiler:alquiler_detalle', args=[alquiler.pk])
            mensaje_exito(request, "Afiliado actualizado y sacado de la lista de espera.")
            return redirect(detalle_alquiler_url)

    pago_alquiler = obtener_pago_alquiler(alquiler)
    pago_form = PagoAlquilerForm(instance=pago_alquiler) if pago_alquiler else None

    context = {
        'titulo': "Reemplazo de afiliado",
        'listaEspera': lista_espera,
        'pago_form': pago_form,
        'filter_form': get_filtro_roles(request)
    }
    return render(request, 'alquiler_reemplazar_inquilino.html', context)


def actualizar_alquiler_y_pago(alquiler, nuevo_afiliado, post_data):
    alquiler.afiliado = nuevo_afiliado
    alquiler.lista_espera.remove(nuevo_afiliado)
    alquiler.cambio_inquilino = True

    pago_alquiler = obtener_pago_alquiler(alquiler)
    alquiler.fecha_solicitud = timezone.now()
    alquiler.save()
    if pago_alquiler:
        pago_form = PagoAlquilerForm(post_data, instance=pago_alquiler)
        if pago_form.is_valid():
            pago_form.fecha_pago = timezone.now()
            pago_form.save()



def obtener_pago_alquiler(alquiler):
    return Pago_alquiler.objects.filter(alquiler=alquiler).first()

def quitar_lista_alquiler(request, alquiler_pk, afiliado_pk):
    alquiler = get_object_or_404(Alquiler, pk=alquiler_pk)
    afiliado = get_object_or_404(Afiliado, pk=afiliado_pk)

    # Remover el afiliado de la lista de espera del alquiler
    alquiler.lista_espera.remove(afiliado)

    mensaje_exito(request, "Afiliado sacado de la lista de espera con exito.")
    detalle_alquiler_url = reverse('alquiler:alquiler_detalle', args=[alquiler.pk])
    return redirect(detalle_alquiler_url)


def alquiler_eliminar(request, pk):
    alquiler = get_object_or_404(Alquiler, pk=pk)

    if alquiler.estado == 1:
        alquiler.fechaBaja = timezone.now()
        alquiler.estado = 4
        alquiler.save()
        mensaje_exito(request, f'El alquiler se ha cancelado con exito')
    else:
        mensaje_error(request, f'No se puede dar de baja el alquiler porque esta vigente')

    return redirect('alquiler:alquiler_detalle', pk=pk)


class AlquilieresListView(PermissionRequiredMixin, LoginRequiredMixin, ListFilterView):
    model = Alquiler
    #paginate_by = MAXIMO_PAGINATOR
    filter_class = AlquilerFilterForm
    success_url = reverse_lazy('alquiler:alquiler_listar')
    template_name = 'alquiler_list.html'
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = get_filtro_roles(self.request)
        # context['titulo'] = "Listado de Alquileres"
        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Aplicar los filtros si se han enviado
        filter_form = AlquilerFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = filter_form.filter_queryset(queryset)
        return queryset
    
    def get_success_url(self):
        if self.request.POST['submit'] == "Guardar y Crear Alquiler":
            return reverse_lazy('alquiler:alquiler_crear', args=[self.object.pk])
        return super().get_success_url()    
    
    def alquiler_confirm_delete (request, pk):
        alquiler = Alquiler.objects.get(pk=pk)
        return render (request,'alquileres/alquiler_confirm_delete.html',{'alquiler':alquiler})
    
# ----------------------------- DETAIL DE ALQUILER  ----------------------------------- #
class AlquilerDetailView (LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Alquiler
    template_name = 'alquiler_detail.html'
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenemos el objeto Alquiler actual
        alquiler = self.object

        # Intentamos obtener el objeto Pago_alquiler asociado al alquiler actual
        pago = Pago_alquiler.objects.filter(alquiler=alquiler).first()  # Intentamos obtener el primer Pago_alquiler asociado, si existe

        # Agregamos el objeto Pago_alquiler al contexto
        context['pago'] = pago
        context['titulo'] = "Detalle de alquiler"
        context['tituloListado1'] = "Lista de espera"
        context['filter_form'] = get_filtro_roles(self.request)
        return context
    
    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
    

# ----------------------------- CREATE DE PAGO  ----------------------------------- #

class PagoAlquilerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Pago_alquiler
    form_class = PagoForm
    template_name = 'pago_form.html'
    success_url = reverse_lazy('alquiler:alquiler_listar')
    permission_required = 'alquileres.permission_gestion_alquiler'
    login_url = '/home/'
    title = "Formulario Alta de Pago"



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.title  # Agrega el título al contexto
        alquileres_sin_pagos = Pago_alquiler.alquileres_sin_pago  # Obtener todos los alquileres sin pago
        context['alquileres_sin_pagos'] = alquileres_sin_pagos  # Pasarlos al contexto
        # Verificar si hay alguna actividad
        return context

    
    def form_valid(self, form):
        messages.success(self.request, f'{ICON_CHECK} Alta de pago exitosa!')
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.warning(self.request, '<i class="fa-solid fa-triangle-exclamation fa-flip"></i> Por favor, corrija los errores a continuación.')
        return super().form_invalid(form)






