from django import forms

from apps.cursos.lookups import ActividadNombreLookup
from ..models import Actividad
from sec2.utils import FiltrosForm
from utils.constants import *
from utils.choices import *
from django import forms
from django.contrib import messages
from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

#------------------ ACTIVIDAD --------------------
class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = '__all__'
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        nombre_lower = nombre.lower()  # Convertir a minúsculas
        existe_actividad = Actividad.objects.filter(nombre__iexact=nombre_lower).exists()
        if existe_actividad:
            raise forms.ValidationError('El nombre de la actividad ya existe. Por favor, elige otro nombre.')
        return nombre

## ------------ FILTRO PARA ACTIVIDAD --------------
class ActividadFilterForm(FiltrosForm):
    nombre = AutoCompleteSelectField(
        lookup_class=ActividadNombreLookup,
        label="Nombre",
        required=False,
        widget=AutoComboboxSelectWidget(ActividadNombreLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )