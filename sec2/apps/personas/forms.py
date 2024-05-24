from turtle import textinput
from apps.personas.lookups import RolLookup
from apps.personas.models import Persona
from django.forms import ModelForm, modelformset_factory, ValidationError, BaseFormSet
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from selectable.forms import AutoCompleteSelectField
from django import forms


class PersonaForm(ModelForm):
    class Meta:
        model = Persona
        fields = '__all__'
        exclude=['persona', 'tipo']
        Widgets ={
            'fechaNacimiento': forms.DateInput(attrs={'type':'datetime-local'}),

            }
          
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
PersonaForm.base_fields.update(PersonaForm.base_fields)

class PersonaUpdateForm(ModelForm):
    class Meta:
        model = Persona  # Asocia el formulario al modelo Persona
        fields = ['dni', 'cuil', 'nombre', 'apellido', 'fecha_nacimiento', 'celular', 'direccion', 'nacionalidad', 'mail', 'estado_civil']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
          }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dni'].widget.attrs['readonly'] = True
        self.fields['cuil'].widget.attrs['readonly'] = True


from django import forms
from dal import autocomplete  # Asegúrate de tener django-autocomplete-light instalado
from tkinter.ttk import Widget
from django_select2 import forms as s2forms
from selectable.forms import AutoCompleteWidget

class PersonaWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "dni__icontains",
        "nombre__icontains",
        "apellido__icontains",
    ]

from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

class RolFilterForm(forms.Form):
    dni = AutoCompleteSelectField(
        lookup_class=RolLookup,
        required=False,
        widget=AutoComboboxSelectWidget(RolLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    def get_selected_rol(self):
        selected_rol = None
        if self.is_valid():
            selected_rol = self.cleaned_data.get('dni')
        return selected_rol
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dni'].widget.attrs.update({'placeholder': 'Buscar Dni/nombre/apellido'})

