from django import forms
from apps.cursos.lookups import ApellidoAlumnoLookup, DniAlumnoLookup
from apps.cursos.models import Alumno
from apps.personas.models import Persona
from datetime import date

from sec2.utils import FiltrosForm

#-------------- Fusion de formulario Alumno y Persona----------------
class AlumnoPersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['dni', 'cuil', 'nombre', 'apellido', 'fecha_nacimiento', 'celular', 'direccion', 'nacionalidad', 'mail', 'estado_civil']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

class AlumnoFilterForm(FiltrosForm):
    persona__dni = AutoCompleteSelectField(
        lookup_class=DniAlumnoLookup,
        label="Dni",
        required=False,
        widget=AutoComboboxSelectWidget(DniAlumnoLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    persona__apellido = AutoCompleteSelectField(
        lookup_class=ApellidoAlumnoLookup,
        label="Apellido",
        required=False,
        widget=AutoComboboxSelectWidget(ApellidoAlumnoLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )