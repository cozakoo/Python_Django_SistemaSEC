from django import forms
from django.forms import ValidationError
from apps.cursos.models import Alumno
from apps.personas.forms import PersonaForm,PersonaUpdateForm
from apps.personas.models import Persona
from .models import Aula, Profesor, Dictado, Curso, Titular, Pago_alumno, Actividad
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML
from sec2.utils import FiltrosForm
from utils.constants import *



class AlumnosDelDictadoFilterForm(FiltrosForm):
    persona__nombre  = forms.CharField(required=False)
    persona__apellido =forms.CharField(required=False)
    persona__dni  = forms.CharField(required=False)

    Submit('submit', 'Guardar', css_class='button white')

class ProfesorDelDictadoFilterForm(FiltrosForm):
    profesor__persona__nombre  = forms.CharField(required=False)
    profesor__persona__apellido =forms.CharField(required=False)

    Submit('submit', 'Guardar', css_class='button white')
