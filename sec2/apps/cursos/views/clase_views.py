from datetime import timedelta
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from apps.afiliados.views import redireccionar_detalle_rol
from sec2.utils import ListFilterView, get_filtro_roles, get_selected_rol_pk
from django.contrib import messages
from ..models import Clase, Dictado, Aula, Horario, Profesor, Reserva, Titular
from ..forms.clase_forms import *
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required , login_required 

# --------------- CREACION DE CLASE --------------------------------
@permission_required('cursos.permission_gestion_curso', raise_exception=True)
@login_required(login_url='/login/')
def generar_clases(request, curso_pk, dictado_id):
    # Obtén el objeto Dictado
    dictado = get_object_or_404(Dictado, pk=dictado_id)

    # Obtén todas las reservas asociadas a ese dictado
    reservas = Reserva.objects.filter(horario__dictado=dictado)

    # Crea una instancia de Clase por cada reserva
    for reserva in reservas:
        Clase.objects.create(reserva=reserva)

    messages.success(request, f'{ICON_CHECK}  Se generaron las clases para el dictado')
    url_dictado_detalle = reverse('cursos:dictado_detalle', kwargs={'curso_pk': curso_pk, 'dictado_pk': dictado_id})
    return redirect(url_dictado_detalle)

# --------------- CLASE DETALLE --------------------------------
class ClaseDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Clase
    template_name = "clase/clase_detail.html"
    permission_required = 'cursos.permission_gestion_curso'
    login_url = '/home/'


    def get_object(self, queryset=None):
        curso_pk = self.kwargs.get("curso_pk")
        dictado_pk = self.kwargs.get("dictado_pk")
        clase_pk = self.kwargs.get("clase_pk")
        return get_object_or_404(
            Clase, reserva__horario__dictado__curso__pk=curso_pk, reserva__horario__dictado__pk=dictado_pk, pk=clase_pk
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        clase = self.object #El objeto clase
        dictado = get_object_or_404(Dictado, id=self.kwargs.get("dictado_pk"))

        context["clase"] = clase
        context["dictado"] = dictado
        context["titulo"] = "Detalle de clase"
        context["tituloListado"] = "Asistencia"
        context["tituloListado1"] = "Alumnos"
        context["tituloListado2"] = "Profesor"
        context['filter_form'] = get_filtro_roles(self.request)

        # Obtener la lista de inscritos en el dictado
        afiliados_inscritos = dictado.afiliados.all()
        familiares_inscritos = dictado.familiares.all()
        profesores_inscritos = dictado.profesores_dictados_inscriptos.all()
        alumnos_inscritos = dictado.alumnos.all()
        # Combino todos los objetos en una lista
        # todos_inscritos = list(afiliados_inscritos) + list(profesores_inscritos) + list(alumnos_inscritos)  
        todos_inscritos = list(afiliados_inscritos) + list(familiares_inscritos) + list(profesores_inscritos) + list(alumnos_inscritos)        
        context["inscritos"] = todos_inscritos

        alumnos_asistieron = clase.asistencia.all()
        alumnos_asistieron_personas = alumnos_asistieron.values_list('persona', flat=True)
        context["lista_asistencia"] = alumnos_asistieron_personas

        # Obtener los titulares asociados al dictado de la clase
        titulares = Titular.objects.filter(dictado=dictado).select_related('profesor')
        context["titulares"] = titulares
        titulares_asistieron = clase.asistencia_profesor.all()
        titulares_asistieron_personas = titulares_asistieron.values_list('persona', flat=True)
        context["lista_asistencia_titular"] = titulares_asistieron_personas

        return context

    def get(self, request, *args, **kwargs):
        filter_rol = get_filtro_roles(request)
        rol = get_selected_rol_pk(filter_rol)

        if rol is not None:
            return redireccionar_detalle_rol(rol)

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        clase = self.get_object()
        if not clase.asistencia_tomada:
            # Marcar la asistencia para todos los alumnos inscritos en el curso
            clase.asistencia.set(clase.reserva.horario.dictado.alumnos.all())
            clase.asistencia_tomada = True
            clase.save()
            # Puedes realizar otras acciones aquí, como guardar el registro en la base de datos
        return HttpResponseRedirect(self.request.path_info)
