from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView 
from django.urls import reverse_lazy
from django.views.generic import View, CreateView , ListView
from apps.afiliados.models import Afiliado
from apps.afiliados.views import redireccionar_detalle_rol
from apps.alquileres.models import Alquiler
from apps.cursos.models import Curso
from sec2.utils import get_filtro_roles, get_selected_rol_pk
from .forms import CustomLoginForm, UserRegisterForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User,Permission
from django.contrib.auth.models import AbstractUser
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

def obtener_permisos_user_string(user):
    permisos = user.user_permissions.all()
    nombres_permisos = [permiso.codename for permiso in permisos]
    return nombres_permisos
        # Imprimir los nombres de los permisos

def obtenerPermisoUsuarios():
      content_type = ContentType.objects.get_for_model(User)
      permiso, creado = Permission.objects.get_or_create(
                                                          codename='permission_gestion_usuario',
                                                          name='Control total user',
                                                          content_type=content_type,          
                                                        )
      return permiso
        




class CustomLoginView(LoginView, View):
    template_name = 'login_acceso.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('home')
    
    def get(self, request, *args: str, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')

        return super().get(request, *args, **kwargs)


def cerrar_session(request):
    logout(request)
    return redirect('users:login')

def actualizar_permisos(request, pk):
    if request.method == 'POST':
            form = request.POST  
          
           #recuperoUsuario
            try:
                user = User.objects.get(pk = pk)   
    
            except User.DoesNotExist:
                    messages.error(request,"no se pude completar operacion")
                    return redirect('users:user_listado')
            
            print(user)
            print(form.get('permiso_afiliado'))
            
            print(form.get('permiso_curso'))

            print(form.get('permiso_alquiler'))

            print(form.get('permiso_administrador'))
            if form.get('permiso_afiliado') == 'on':
                    permiso = Permission.objects.get(codename='permission_gestion_afiliado')
                    user.user_permissions.add(permiso)
            else:
                 print("entre quitar permiso")
                 permiso = Permission.objects.get(codename='permission_gestion_afiliado')
                 user.user_permissions.remove(permiso)
                 user.save()  

            if form.get('permiso_curso') :
                    permiso = Permission.objects.get(codename='permission_gestion_curso')
                    user.user_permissions.add(permiso)
            else: 
                    permiso = Permission.objects.get(codename='permission_gestion_curso')
                    user.user_permissions.remove(permiso)        
            
            if form.get('permiso_alquiler') :
                    permiso = Permission.objects.get(codename='permission_gestion_alquiler')
                    user.user_permissions.add(permiso)
            else:
                    permiso = Permission.objects.get(codename='permission_gestion_alquiler')
                    user.user_permissions.remove(permiso)
                    

            if form.get('permiso_administrador') :
                    permiso = obtenerPermisoUsuarios()
                    user.user_permissions.add(permiso)
            else:
                    permiso = obtenerPermisoUsuarios()
                    user.user_permissions.remove(permiso)
            user.is_superuser = False
            user.save()        
            messages.success(request, 'Permisos de Usuario Actualizados exitosamente')
    return redirect('users:user_listado')

class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = '/login/'
    model = User
    template_name ='listado_usuarios.html'
    permission_required = "auth.permission_gestion_usuario"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        # filter_form = UserFilterForm(self.request.GET)

        # if filter_form.is_valid():
        #     username = filter_form.cleaned_data.get('username')
        #     is_active_values = filter_form.cleaned_data.get('is_active')  # Obtenemos los valores seleccionados

        #     if username:
        #         queryset = queryset.filter(username__icontains=username)

        #     if is_active_values:
        #         # Convertimos los valores seleccionados a booleanos
        #         is_active_values = [bool(int(value)) for value in is_active_values]
        #         queryset = queryset.filter(is_active__in=is_active_values)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permisos = obtener_permisos_user_string(self.request.user)
        context['titulo'] = 'Listado de Usuarios'
        context['permisos'] = permisos
        context['filter_form'] = get_filtro_roles(self.request)
        # context['filter_form'] = UserFilterForm(self.request.GET)
        return context



class CreacionUsuarios(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'creacion_usuarios.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('home')
    login_url = '/login/'
    permission_required = "auth.permission_gestion_usuario"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permisos = obtener_permisos_user_string(self.request.user)
        
        context['permisos'] = permisos
        context['titulo'] = "Registro de usuario"
        context['filter_form'] = get_filtro_roles(self.request)
        return context

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)
        
        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
     
    def form_valid(self, form):
        # Aquí puedes acceder a los datos del formulario
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        email = form.cleaned_data['email']
        form.save() 
        user = User.objects.get(username=username)

        if form.cleaned_data['permiso_gestion_afiliados'] :
                permiso = Permission.objects.get(codename='permission_gestion_afiliado')
                user.user_permissions.add(permiso)

        if form.cleaned_data['permiso_gestion_cursos'] :
                permiso = Permission.objects.get(codename='permission_gestion_curso')
                user.user_permissions.add(permiso)
        
        if form.cleaned_data['permiso_gestion_salon'] :
                permiso = Permission.objects.get(codename='permission_gestion_alquiler')
                user.user_permissions.add(permiso)

        if form.cleaned_data['permiso_gestion_usuarios'] :
                permiso = obtenerPermisoUsuarios()
                user.user_permissions.add(permiso)

        user.save()        
        messages.success(self.request, 'Usuario creado exitosamente')
        return redirect('users:user_register')
        
       
    
  
     
    
