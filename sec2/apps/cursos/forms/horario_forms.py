from django import forms
from ..models import Horario, Aula
from utils.constants import *
from django import forms
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _
import datetime
from datetime import date


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['dia_semana', 'hora_inicio']
        widgets = {
            'hora_inicio': forms.TimeInput(format='%H:%M')
        }

    def clean_hora_inicio(self):
        hora_inicio = self.cleaned_data['hora_inicio']

        # Define la hora mínima y máxima permitida
        hora_minima = datetime.time(8, 0)
        hora_maxima = datetime.time(21, 0)

        # Verifica que los minutos sean 0 o 30
        if hora_inicio.minute not in [0, 30]:
            raise ValidationError(_('Los minutos de la hora de inicio deben ser 0 o 30.'))

        # Verifica si la hora de inicio está fuera del rango permitido
        if hora_inicio < hora_minima or hora_inicio >= hora_maxima:
            raise ValidationError(_('La hora de inicio debe estar en el rango de 8:00 a 20:00.'))

        return hora_inicio