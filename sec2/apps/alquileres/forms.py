from django import forms
from apps.afiliados.lookups import AfiLookup
from apps.alquileres.lookups import DniEncargadoLookup, EncargadoLookup, SalonLookup, ServicioNombreLookup
from apps.personas.models import Persona
from utils.choices import ESTADO_CIVIL, LOCALIDADES_CHUBUT, MAX_LENGTHS, NACIONALIDADES
from .models import Salon, Servicio, Alquiler, Pago_alquiler
from sec2.utils import FiltrosForm
from utils.constants import *
from datetime import date



# ----------------------------- ENCARGADO  ----------------------------------- #
class EncargadorForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['dni', 'cuil', 'nombre', 'apellido', 'fecha_nacimiento', 'celular', 'direccion', 'nacionalidad', 'mail', 'estado_civil']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
   
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        edad = date.today().year - fecha_nacimiento.year
        if edad < 18 or edad >= 100:
            raise forms.ValidationError("Debes ser mayor de 18 años y menor de 100 años.")
        return fecha_nacimiento

from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

class EncargadoFilterForm(FiltrosForm):
    persona__dni = AutoCompleteSelectField(
        lookup_class=DniEncargadoLookup,
        required=False,
        label="Dni",
        widget=AutoComboboxSelectWidget(DniEncargadoLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )

class EncargadoUpdateForm(forms.ModelForm):

    class Meta:
        model = Persona
        fields = '__all__'
        exclude = ['tipo', 'hasta', 'persona']
        labels = {
            'ejerce_desde': "Fecha desde que empezo a ejercer",
        }

    def __init__(self, *args, **kwargs):
        super(EncargadoUpdateForm, self).__init__(*args, **kwargs)
        persona_fields = ['dni', 'cuil', 'nombre', 'apellido', 'fecha_nacimiento', 'celular', 'direccion', 'nacionalidad', 'mail', 'estado_civil']
        for field_name in persona_fields:
            if field_name == 'fecha_nacimiento':
                self.fields[field_name] = forms.DateField(
                    required=True,
                    initial=getattr(self.instance.persona, field_name),
                )
            elif field_name == 'estado_civil':
                self.fields[field_name] = forms.ChoiceField(
                    choices=ESTADO_CIVIL,
                    required=True,
                    initial=getattr(self.instance.persona, field_name),
                )
            elif field_name == 'nacionalidad':
                self.fields[field_name] = forms.ChoiceField(
                    choices=NACIONALIDADES,
                    required=True,
                    initial=getattr(self.instance.persona, field_name),
                )
            elif field_name in MAX_LENGTHS:
                max_length = MAX_LENGTHS[field_name]
                self.fields[field_name] = forms.CharField(
                    max_length=max_length,
                    required=True,
                    initial=getattr(self.instance.persona, field_name),
                    help_text=getattr(self.instance.persona._meta.get_field(field_name), 'help_text', '')
                )
            else:
                self.fields[field_name] = forms.CharField(
                    required=True,
                    initial=getattr(self.instance.persona, field_name),
                    help_text=getattr(self.instance.persona._meta.get_field(field_name), 'help_text', '')
                )
            self.fields[field_name].widget.attrs['readonly'] = False
        self.fields['dni'].widget.attrs['readonly'] = True
        self.fields['cuil'].widget.attrs['readonly'] = True


# -----------------------------  SERVICIO  ----------------------------------- #
class ServiciorForm(forms.ModelForm):    
    class Meta:
        model = Servicio
        fields = ('nombre',)
        widgets = {
           'nombre': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Eje: Cubiertos 50'}),
            }
    

class ServicioFilterForm(FiltrosForm):
    nombre = AutoCompleteSelectField(
        lookup_class=ServicioNombreLookup,
        label="Nombre",
        required=False,
        widget=AutoComboboxSelectWidget(ServicioNombreLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
# ----------------------------- SALON  ----------------------------------- #
from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

class SalonrForm(forms.ModelForm):
    encargado = AutoCompleteSelectField(
        lookup_class=EncargadoLookup,
        required=False,
        widget=AutoComboboxSelectWidget(EncargadoLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    class Meta:
        model = Salon
        fields = ('nombre', 'localidad', 'direccion', 'capacidad', 'precio','tipo_salon','servicios', 'encargado')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Eje: PasaRatos'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Eje: Pedro Pascal 150'}),
            'capacidad': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Eje: 50'}),
            'tipo_salon': forms.RadioSelect(attrs={'class': 'tipo_salon-radio'}),  # Agrega la clase CSS personalizada al widget del campo de turno

            #'encargado': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'encargado'}),
            'precio': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Eje: 1000'}),
            'servicios': forms.CheckboxSelectMultiple(attrs={'class': 'servicios-checkbox'}), 
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_salon'].choices = [(1, 'Polideportivo'), (2, 'Multiuso')]



class SalonFilterForm(FiltrosForm):
    nombre = forms.CharField(required=False)
    localidad = forms.ChoiceField(required=False, choices=LOCALIDADES_CHUBUT, label='Localidad')
    capacidad = forms.IntegerField(required=False, label='Capacidad mínima')
    
# ----------------------------- ALQUILER ----------------------------------- #

class AlquilerForm(forms.ModelForm):

    afiliado = AutoCompleteSelectField(
        lookup_class=AfiLookup,
        required=True,
        widget=AutoComboboxSelectWidget(AfiLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    salon = AutoCompleteSelectField(
        lookup_class=SalonLookup,
        required=True,
        widget=AutoComboboxSelectWidget(SalonLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    turno = forms.ChoiceField(
        required=True,
        label='Turno',
        choices=(('Mañana', 'Mañana'), ('Noche', 'Noche')),
        widget=forms.RadioSelect(attrs={'class': 'two-columns'})
    )
    class Meta:
        model = Alquiler
        fields = ('afiliado', 'salon', 'turno', 'seguro','fecha_alquiler')
        widgets = {
           'fecha_alquiler': forms.DateInput(attrs={'type': 'date'}),
           'seguro': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Eje: 1000'}),
       }
    def __init__(self, *args, **kwargs):
        super(AlquilerForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        afiliado = cleaned_data.get("afiliado")
        salon = cleaned_data.get("salon")
        turno = cleaned_data.get("turno")
        seguro = cleaned_data.get("seguro")
        fecha_alquiler = cleaned_data.get("fecha_alquiler")

        # Verifica si algún campo requerido está vacío
        if not afiliado:
            self.add_error('afiliado', 'Este campo es obligatorio.')
        if not salon:
            self.add_error('salon', 'Este campo es obligatorio.')
        if not turno:
            self.add_error('turno', 'Este campo es obligatorio.')
        if not seguro:
            self.add_error('seguro', 'Este campo es obligatorio.')
        if not fecha_alquiler:
            self.add_error('fecha_alquiler', 'Este campo es obligatorio.')
        
        return cleaned_data

class AlquilerFilterForm(FiltrosForm):
    alquiler_salon_nombre = forms.CharField(required=False)
    fecha_alquiler = forms.DateField(required=False)
    turno = forms.CharField(required=False)


# ----------------------------- PAGO ----------------------------------- #
class PagoForm(forms.ModelForm):
    # forma_pago = forms.ChoiceField(choices=[('total', 'Total'), ('cuota', 'Cuota')])
    alquiler = forms.ChoiceField(choices=[])
   

    class Meta:
        model = Pago_alquiler
        fields = ('forma_pago', 'alquiler')
        widgets = {
            'forma_pago': forms.RadioSelect(attrs={'class': 'turno-radio'}),  # Agrega la clase CSS personalizada al widget del campo de turno

           #'fecha_solicitud': forms.DateInput(attrs={'type': 'date'}),
           #'fecha_alquiler': forms.DateInput(attrs={'type': 'date'}),
           #'seguro': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Eje: 1000'}),   
       }
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        alquileres_sin_pagos = Pago_alquiler.alquileres_sin_pago()
        choices = [(alquiler.id, f'{alquiler.afiliado.persona.nombre} - {alquiler.salon.nombre} - {alquiler.fecha_alquiler.strftime("%d/%m/%Y")} - {alquiler.turno}') for alquiler in alquileres_sin_pagos]
        self.fields['alquiler'].choices = choices
        self.fields['forma_pago'].choices = [('total', 'Total'), ('cuota', 'Cuota')]


    def clean_alquiler(self):
        alquiler_id = self.cleaned_data['alquiler']
        try:
            alquiler = Alquiler.objects.get(pk=alquiler_id)
            return alquiler
        except Alquiler.DoesNotExist:
            raise forms.ValidationError("El alquiler seleccionado no es válido.")
        
class AlquilerFilterForm(FiltrosForm):
    salon = AutoCompleteSelectField(
        lookup_class=SalonLookup,
        required=False,
        widget=AutoComboboxSelectWidget(SalonLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )

    turno = forms.ChoiceField(
        required=False,
        label='Turno',
        choices=(('Mañana', 'Mañana'), ('Noche', 'Noche')),
        widget=forms.RadioSelect
    )
    cambio_inquilino = forms.BooleanField(required=False, label='Cambio de Inquilino')
    estado = forms.MultipleChoiceField(
        required=False,
        label='Estado del Alquiler',
        choices=Alquiler.ESTADOS,
        widget=forms.CheckboxSelectMultiple
    )
    def filter_queryset(self, queryset):
        if self.is_valid():
            # Aplicar filtros si están presentes en el formulario
            if self.cleaned_data['salon']:
                queryset = queryset.filter(salon=self.cleaned_data['salon'])
            if self.cleaned_data['turno']:
                queryset = queryset.filter(turno=self.cleaned_data['turno'])
            if self.cleaned_data['cambio_inquilino']:
                queryset = queryset.filter(cambio_inquilino=self.cleaned_data['cambio_inquilino'])
            if self.cleaned_data['estado']:
                queryset = queryset.filter(estado__in=self.cleaned_data['estado'])
        return queryset

class PagoAlquilerForm(forms.ModelForm):
    class Meta:
        model = Pago_alquiler
        fields = ['forma_pago']