from django import forms
# from ..models import Aula, Clase, Dictado, Horario
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML
from sec2.utils import FiltrosForm
from utils.constants import *
from django.shortcuts import get_object_or_404
from datetime import date
from django.db.models import Q
from django.core.exceptions import ValidationError

## ------------ FORMULARIO DE CLASE --------------
# class ClaseForm(forms.ModelForm):
#     class Meta:
#         model = Clase
#         fields = '__all__'
#         exclude = ['dictado', 'inscritos']
#         # exclude = ['dictado', 'inscritos', 'aula']
        
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Agrega el widget DateInput para el campo 'fecha'
#         self.fields['fecha'].widget = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
#         # Validación para permitir solo fechas mayores o iguales a hoy
#         self.fields['fecha'].widget.attrs['min'] = str(date.today())
#         # Deshabilitar los domingos
#         self.fields['fecha'].widget.attrs['class'] = 'datepicker'

#     def clean_fecha(self):
#         fecha = self.cleaned_data['fecha']
#         dictado = self.instance.dictado
#         horarios_dictado = self.horarios_dictado  # Accede a los horarios desde el contexto

#         # Obtener el día de la semana de la fecha seleccionada (0 para lunes, 1 para martes, etc.)
#         dia_semana_fecha = fecha.weekday()
#         # Verificar si hay al menos un horario cuyo día sea igual a la fecha seleccionada
#         if not any(horario.dia_semana == dia_semana_fecha for horario in horarios_dictado):
#             raise ValidationError("La fecha seleccionada no está habilitada para este dictado.")

#         return fecha
    
# class ClaseFilterForm (FiltrosForm):
#     dia = forms.DateField(required=False)
#     #actividad = forms.ChoiceField(required=False)