from datetime import timezone
from django import forms

from apps.cursos.lookups import ActividadLookup, ProfesorDniLookup
from apps.personas.lookups import RolLookup
from ..models import Actividad, Curso, Dictado, ListaEspera, PagoAlumno, PagoProfesor
from utils.constants import *
from utils.choices import *
from sec2.utils import FiltrosForm
from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

#----------------------- CURSO --------------------
class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = '__all__'
        exclude= ['es_convenio', 'actividad', 'fechaBaja']

    area = forms.ChoiceField(
        choices=[('', '---------')] + AREAS,  # Agrega el valor por defecto a las opciones de AREAS
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )
    actividad = AutoCompleteSelectField(
        lookup_class=ActividadLookup,
        required=False,
        widget=AutoComboboxSelectWidget(ActividadLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        nombre_lower = nombre.lower()  # Convertir a minúsculas

        # Exclude the current instance from the queryset (assuming instance is available in the form)
        curso_id = self.instance.id if self.instance else None

        existe_curso = Curso.objects.filter(nombre__iexact=nombre_lower).exclude(id=curso_id).exists()

        if existe_curso:
            raise forms.ValidationError('El nombre del curso ya existe. Por favor, elige otro nombre.')

        return nombre
    
    def __init__(self, *args, **kwargs):
        super(CursoForm, self).__init__(*args, **kwargs)
        # self.fields['actividad'].label = 'Actividad'
        # self.fields['actividad'].queryset = Actividad.objects.all().order_by('nombre')
        tipo_curso = kwargs.get('initial', {}).get('tipo_curso')
        if tipo_curso == 'convenio':
            self.fields['area'].initial = 0
            self.fields['area'].widget = forms.HiddenInput()
            self.fields['area'].required = False
            self.fields['precio_total'].initial = 0
        else:
            if tipo_curso == 'sec':
                self.fields['area'].widget = forms.Select(choices=[(0, "Capacitación"), (1, "Cultura")])
                self.fields['area'].required = True
            else:
                if tipo_curso == 'actividad':
                    self.fields['area'].initial = 2
                    self.fields['area'].widget = forms.HiddenInput()
                    self.fields['area'].required = False
                else:
                    self.fields['area'].widget = forms.Select(choices=AREAS)
                    self.fields['area'].required = True

class CursoFilterForm(FiltrosForm):
    nombre = forms.CharField(required=False)
    actividad = forms.ModelChoiceField(
        queryset=Actividad.objects.all().order_by('nombre'),
        label='Actividad',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    area = forms.MultipleChoiceField(
        label='Área',
        choices=list(AREAS),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'})
    )

    es_convenio = forms.BooleanField(
        label='Conv. Provincial',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    

    def clean_duracion(self):
        duracion = self.cleaned_data['duracion']
        try:
            return int(duracion)
        except (ValueError, TypeError):
            # Si no se puede convertir a un número, devuelve None
            return None
        

class ListaEsperaAdminForm(forms.ModelForm):
    class Meta:
        model = ListaEspera
        fields = '__all__'

    def clean_fechaInscripcion(self):
        # Devuelve la fecha y hora actual
        return timezone.now()
    



class PagoProfesorForm(forms.ModelForm):
    class Meta:
        model = PagoProfesor
        fields = ['profesor']


class PagoProfesorFilterForm(FiltrosForm):
    profesor__persona__dni = AutoCompleteSelectField(
        lookup_class=ProfesorDniLookup,
        label="Dni (profesor)",
        required=False,
        widget=AutoComboboxSelectWidget(ProfesorDniLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    profesor__dictados__curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        required=False,
        label='Curso',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    profesor__dictados = forms.ModelChoiceField(
        queryset=Dictado.objects.filter(estado=2),
        required=False,
        label='Dictado',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profesor__dictados'].label_from_instance = self.label_from_instance

    def label_from_instance(self, obj):
        return f'{obj.legajo}'
    
class PagoAlumnoFilterForm(FiltrosForm):
    rol = AutoCompleteSelectField(
        lookup_class=RolLookup,
        label="Dni",
        required=False,
        widget=AutoComboboxSelectWidget(lookup_class=RolLookup, attrs={'class': 'form-control', 'id': 'enc_alumno_aux'})
    )

    # Filtrar por curso relacionado con los dictados de los detalles de pago del alumno
    detalles_pago_alumno__dictado__curso = forms.ModelChoiceField(
        queryset=Curso.objects.all().order_by('nombre'),
        required=False,
        label='Curso',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    detalles_pago_alumno__dictado = forms.ModelChoiceField(
        queryset=Dictado.objects.filter(estado__in=[2, 3]).order_by('legajo'),
        required=False,
        label='Dictado',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['detalles_pago_alumno__dictado'].label_from_instance = self.label_from_instance

    def label_from_instance(self, obj):
        return f'{obj.legajo}'

class PagoRolForm(forms.ModelForm):
    rol = AutoCompleteSelectField(
        lookup_class=RolLookup,
        required=False,
        widget=AutoComboboxSelectWidget(lookup_class=RolLookup, attrs={'class': 'form-control', 'id': 'enc_alumno_aux'})
    )
    class Meta:
        model = PagoAlumno
        fields = ['rol']