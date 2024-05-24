from django import forms
from django.db.models import Q, Model
from decimal import Decimal
from datetime import date
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.list import ListView
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML
from apps.afiliados.models import Afiliado, Familiar, RelacionFamiliar
from apps.alquileres.models import Encargado
from apps.cursos.models import Alumno, Profesor
from apps.personas.forms import RolFilterForm
from apps.personas.models import Rol
from utils.constants import ROL_TIPO_PROFESOR

def dict_to_query(filtros_dict):
    filtro = Q()
    for attr, value in filtros_dict.items():
        if not value:
            continue
        if type(value) == str:
            if value.isdigit():
                prev_value = value
                value = int(value)
                filtro &= Q(**{attr: value}) | Q(**
                                                 {f'{attr}__icontains': prev_value})
            else:
                attr = f'{attr}__icontains'
                filtro &= Q(**{attr: value})
        # elif isinstance(value, Model) or isinstance(value, int) or isinstance(value, Decimal):
        elif isinstance(value, (Model, int, Decimal, date)):
            filtro &= Q(**{attr: value})
    return filtro


from crispy_forms.layout import HTML

class FiltrosForm(forms.Form):
    orden = forms.CharField(required=False)

    def filter(self, qs, filters):
        return qs.filter(dict_to_query(filters))  # aplicamos filtros

    def sort(self, qs, ordering):
        for o in ordering.split(','):
            if o != '':
                qs = qs.order_by(o)  # aplicamos ordenamiento
        return qs

    def apply(self, qs):
        if self.is_valid():
            cleaned_data = self.cleaned_data
            ordering = cleaned_data.pop("orden", None)
            if len(cleaned_data) > 0:
                qs = self.filter(qs, cleaned_data)
            if ordering:
                qs = self.sort(qs, ordering)
        return qs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        fields = list(self.fields.keys())
        fields = list(filter(lambda f: f != 'orden', fields))
        
        # Agregar un botón "Clear" que limpia los filtros
        self.helper.layout = Layout(
            *fields,
            HTML('<div class="row">'),
                HTML('<div class="col-md-6 text-center">'),
                    HTML('<button type="submit" class="btn btn-primary">Filtrar</button>'),
                HTML('</div>'),
                
                HTML('<div class="col-md-6">'),
                    HTML('<a class="btn btn-secondary" href="?">Borrar</a>'),
                HTML('</div>'),
            HTML('</div>')
        )
class ListFilterView(ListView):
    filter_class = None
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.filter_class:
            context['filtros'] = self.filter_class(self.request.GET)
            context['query'] = self.get_queryset()
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.filter_class:
            filtros = self.filter_class(self.request.GET)
            return filtros.apply(qs)
        return qs
   
def get_filtro_roles(request):
    return RolFilterForm(request.GET)

def get_selected_rol_pk(filter_form):
    selected_rol_pk = None
    if filter_form.is_valid():
        selected_rol = filter_form.get_selected_rol()
        if selected_rol:
            selected_rol_pk = selected_rol.pk
            return get_object_or_404(Rol, pk=selected_rol_pk)
    return None


def redireccionarDetalleRol(rol):
    tipo = rol.tipo

    if tipo == 1:
        afiliado = get_object_or_404(Afiliado, persona__pk=rol.persona.pk)
        return redirect('afiliados:afiliado_detalle', pk=afiliado.pk)

    elif tipo == 2:
        grupoFamiliar = get_object_or_404(Familiar, persona__pk=rol.persona.pk)
        relacion_familiar = RelacionFamiliar.objects.filter(familiar=grupoFamiliar).first()
        return redirect('afiliados:familiar_detalle', pk=relacion_familiar.afiliado.pk, familiar_pk=grupoFamiliar.pk)

    elif tipo == 3:
        alumno = get_object_or_404(Alumno, persona__pk=rol.persona.pk)
        return redirect('cursos:alumno_detalle', pk=alumno.pk)

    elif tipo == ROL_TIPO_PROFESOR:
        profesor = get_object_or_404(Profesor, persona__pk=rol.persona.pk)
        return redirect('cursos:profesor_detalle', pk=profesor.pk)

    elif tipo == 5:
        encargado = get_object_or_404(Encargado, persona__pk=rol.persona.pk)
        return redirect('alquiler:encargado_detalle', pk=encargado.pk)
    return redirect('home')
    