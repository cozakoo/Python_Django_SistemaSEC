from django import forms
from ..models import Aula
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML
from sec2.utils import FiltrosForm
from utils.constants import *
from utils.choices import *
from django.urls import reverse

## ------------ FORMULARIO DE AULA --------------
class AulaForm(forms.ModelForm):
    tipo = forms.ChoiceField(
        choices=TIPO_AULA,
        widget=forms.RadioSelect,
        label='Tipo de aula'
    )
    
    class Meta:
        model = Aula
        fields = '__all__'

    def clean_tipo(self):
        tipo = self.cleaned_data['tipo']
        tipo = tipo.lower()
        return tipo


    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        numero = cleaned_data.get('numero')

        # Verificar si ya existe un aula con el mismo tipo y número
        existing_aula = Aula.objects.filter(tipo=tipo, numero=numero).exclude(id=self.instance.id if self.instance else None).first()

        if existing_aula:
            raise forms.ValidationError("Ya existe un aula con el mismo tipo y número.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

## ------------ FILTRO PARA AULA --------------
class AulaFilterForm(FiltrosForm):
    capacidad = forms.IntegerField(required=False, label='Capacidad deseada')
    tipo = forms.ChoiceField(
        choices=TIPO_AULA,
        required=False,
        label='Tipo de aula',
        widget=forms.RadioSelect()  # Utilizamos RadioSelect para mostrar los botones de radio

    )