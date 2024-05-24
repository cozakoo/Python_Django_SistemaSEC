# from sec2.sec2.lookups import AfiliadosLookup
from apps.personas.lookups import RolLookup
from .lookups import AfiLookup, CuitEmpleadorLookup, DniAfiliadoLookup, DniFamiliarLookup
from utils.choices import AFILIADO_ESTADO, ESTADO_CIVIL, LOCALIDADES_CHUBUT, MAX_LENGTHS, NACIONALIDADES, TIPOS_RELACION_FAMILIAR
from utils.funciones import validate_no_mayor_actual
from .models import Afiliado, Familiar, PagoCuota
from apps.personas.models import Persona
from sec2.utils import FiltrosForm
from utils.regularexpressions import *
from utils.constants import *
from django import forms
from django.utils import timezone
import re
from django.core.validators import MinValueValidator
from django.core.validators import EmailValidator
from django import forms

import datetime
from datetime import date

from selectable.forms import AutoCompleteSelectField

from django import forms

from selectable.forms import AutoCompleteWidget

# ---------- Utilizado para el AFILIADO CRATE VIEW 
class AfiliadoPersonaForm(forms.ModelForm):
    razon_social = forms.CharField(max_length=30, validators=[text_and_numeric_validator])
    categoria_laboral = forms.CharField(max_length=50, validators=[text_and_numeric_validator])
    rama = forms.CharField(max_length=50, validators=[text_and_numeric_validator])
    sueldo = forms.IntegerField(validators=[MinValueValidator(0, 'El sueldo debe ser un valor positivo.')])
    horaJornada = forms.IntegerField(
        validators=[MinValueValidator(1)],
                help_text="Total de horas trabajadas a la semana"

    )
    cuit_empleador = forms.CharField(max_length=11, validators=[numeric_validator], help_text='Cuit sin puntos y guiones. Ej: 01234567899')
    domicilio_empresa = forms.CharField(max_length=100, validators=[text_and_numeric_validator], help_text='Calle y numero')
    # fechaAfiliacion = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fechaIngresoTrabajo = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[validate_no_mayor_actual]
    )
    localidad_empresa = forms.ChoiceField(choices=LOCALIDADES_CHUBUT, initial="TRELEW")

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

########### Utilizado para el AFILIADO fliadosListView ##############################################
from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

class AfiliadoFilterForm(FiltrosForm):
    persona__dni = AutoCompleteSelectField(
        lookup_class=DniAfiliadoLookup,
        label="Dni",
        required=False,
        widget=AutoComboboxSelectWidget(DniAfiliadoLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    cuit_empleador = AutoCompleteSelectField(
        lookup_class=CuitEmpleadorLookup,
        label="Cuit empleador",
        required=False,
        widget=AutoComboboxSelectWidget(CuitEmpleadorLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )

    opciones_estado_ordenadas = sorted(AFILIADO_ESTADO, key=lambda x: x[    1])

    estado = forms.MultipleChoiceField(
        required=False,
        choices= opciones_estado_ordenadas,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )
    
########### Utilizado para el AFILIADO UPDATE ##############################################
class AfiliadoUpdateForm(forms.ModelForm):
    class Meta:
        model = Afiliado
        fields = '__all__'
        exclude = ['tipo', 'hasta', 'estado', 'persona', 'fechaAfiliacion']
        labels = {
            'fechaIngresoTrabajo': "Fecha de ingreso al trabajo",
        }

    def __init__(self, *args, **kwargs):
        super(AfiliadoUpdateForm, self).__init__(*args, **kwargs)
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
            self.fields[field_name].widget.attrs['readonly'] = False  # P
        self.fields['dni'].widget.attrs['readonly'] = True
        self.fields['cuil'].widget.attrs['readonly'] = True

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        if fecha_nacimiento > timezone.now().date():
            raise forms.ValidationError('La fecha de nacimiento no puede estar en el futuro.')
        return fecha_nacimiento
    
    def clean_apellido(self):
        apellido = self.cleaned_data['apellido']
        if not apellido.isalpha():
            raise forms.ValidationError('El apellido debe contener solo letras y espacios.')
        return apellido

    def clean_mail(self):
        mail = self.cleaned_data['mail']
        # Expresión regular para validar una dirección de correo electrónico
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, mail):
            raise forms.ValidationError('El correo electrónico no es válido.')
        return mail

    def save(self, commit=True):
        # Actualiza los campos de Afiliado
        afiliado = super().save(commit=False)
        # No olvides guardar los campos de Afiliado aquí, si es necesario
        if commit:
            afiliado.save()
        return afiliado

    def is_valid(self):
        return super(AfiliadoUpdateForm, self).is_valid()

    def clean(self):
        cleaned_data = super(AfiliadoUpdateForm, self).clean()
        return cleaned_data
    

########### FAMILIAR ##############################################
from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

class AfiliadoSelectForm(forms.Form):
    class Meta:
        model = Persona
        fields = ['dni', 'cuil', 'nombre', 'apellido', 'fecha_nacimiento', 'celular', 'direccion', 'nacionalidad', 'mail', 'estado_civil']
        widgets = {
        'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    tipo = forms.ChoiceField(choices=TIPOS_RELACION_FAMILIAR, widget=forms.RadioSelect(attrs={'class': 'tipo-radio'}))
    afiliado = AutoCompleteSelectField(
        lookup_class=AfiLookup,
        required=False,
        widget=AutoComboboxSelectWidget(AfiLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    dni = forms.CharField(
        max_length=8,
        help_text='Sin puntos',
        validators=[
            numeric_validator,
            exact_length_8_validator,
        ]
    )
    cuil = forms.CharField(
        max_length=11,
        help_text='Sin puntos y guiones',
        validators=[
            numeric_validator,
            exact_length_11_validator,
        ]
    )
    nombre = forms.CharField(max_length=30, validators=[text_validator])
    apellido = forms.CharField(max_length=30, validators=[text_validator])
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[
            validate_no_mayor_actual
        ]
    )
    celular = forms.CharField(
        max_length=10,
        validators=[
            numeric_validator,
            exact_length_10_validator,
        ],
        help_text='Ejemplo: 1234567632',
    )
    direccion = forms.CharField(max_length=50, validators=[text_and_numeric_validator], help_text='Calle y numero')
    nacionalidad = forms.ChoiceField(choices=NACIONALIDADES, initial='AR')  # Establecer el valor predeterminado

    mail = forms.EmailField(
        max_length=50,
        validators=[EmailValidator(message='Debe ser un correo válido.')],
        help_text='Debe ser un correo válido.',
    )

    estado_civil = forms.ChoiceField(choices=ESTADO_CIVIL)

    es_afiliado = forms.BooleanField(initial=False, required=False)
    es_alumno = forms.BooleanField(initial=False, required=False)
    es_profesor = forms.BooleanField(initial=False, required=False)
    es_encargado = forms.BooleanField(initial=False, required=False)
    es_grupo_familiar = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(AfiliadoSelectForm, self).__init__(*args, **kwargs)

    def label_from_instance_with_strextra(self, obj):
        return obj.__strextra__()
    
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        edad = date.today().year - fecha_nacimiento.year
        if edad < 18 or edad >= 100:
            raise forms.ValidationError("Debes ser mayor de 18 años y menor de 100 años.")
        return fecha_nacimiento
    
class GrupoFamiliarPersonaForm(forms.ModelForm):

    tipo = forms.ChoiceField(choices=TIPOS_RELACION_FAMILIAR)

    class Meta:
        model = Persona
        fields = ['dni', 'cuil', 'nombre', 'apellido', 'fecha_nacimiento', 'celular', 'direccion', 'nacionalidad', 'mail', 'estado_civil']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        edad = date.today().year - fecha_nacimiento.year
        print("edad",edad)
        if edad < 0 or edad >= 100:
            raise forms.ValidationError("Edad maxima: 100 años")
        return fecha_nacimiento
    
########### FAMILIAR ##############################################
class GrupoFamiliarPersonaUpdateForm(forms.ModelForm):

    class Meta:
        model = Persona
        fields = ['dni', 'cuil', 'nombre', 'apellido', 'fecha_nacimiento', 'celular', 'direccion', 'nacionalidad', 'mail', 'estado_civil']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(GrupoFamiliarPersonaUpdateForm, self).__init__(*args, **kwargs)
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
            self.fields[field_name].widget.attrs['readonly'] = False  # P
        self.fields['dni'].widget.attrs['readonly'] = True
        self.fields['cuil'].widget.attrs['readonly'] = True

########### FILTER FORM FAMILIAR  ##############################################
class RelacionFamiliarFilterForm(FiltrosForm):
    familiar__persona__dni =  AutoCompleteSelectField(
        lookup_class=DniFamiliarLookup,
        label="Dni (familiar)",
        required=False,
        widget=AutoComboboxSelectWidget(DniFamiliarLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    afiliado__persona__dni =  AutoCompleteSelectField(
        lookup_class=DniAfiliadoLookup,
        label="Dni (afiliado)",
        required=False,
        widget=AutoComboboxSelectWidget(DniAfiliadoLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    tipo_relacion = forms.ChoiceField(
        label='Tipo de Relación',
        choices=TIPOS_RELACION_FAMILIAR,
        required=False,
        widget=forms.RadioSelect
    )

class PagoCuotaForm(forms.ModelForm):
    
    afiliado = AutoCompleteSelectField(
        lookup_class=AfiLookup,
        required=False,
        widget=AutoComboboxSelectWidget(AfiLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )


    class Meta:
        model = PagoCuota
        fields = '__all__'
        exclude = ['afiliado']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'pdf_transferencia': forms.FileInput(attrs={'accept': 'application/pdf'}),
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_monto(self):
        monto = self.cleaned_data['monto']
        if monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor que cero.')
        return monto

    def clean_fecha_pago(self):
        fecha_pago = self.cleaned_data.get('fecha_pago')
        today = timezone.now().date()
        if fecha_pago is not None and fecha_pago > today:
            raise forms.ValidationError('La fecha de pago no puede ser superior a la fecha actual.')
        return fecha_pago

    def clean_pdf_transferencia(self):
        pdf_transferencia = self.cleaned_data.get('pdf_transferencia')
        if pdf_transferencia is None:
            return pdf_transferencia  # Return the original cleaned data if no PDF file is provided

        # Opcionalmente, puedes agregar validaciones adicionales para el archivo PDF si es necesario.
        # Por ejemplo, verificar el tamaño del archivo, el tipo, etc.
        return pdf_transferencia

########### FILTER FORM FAMILIAR  ##############################################
class PagoCuotarFilterForm(FiltrosForm):
    afiliado__persona__dni = AutoCompleteSelectField(
        lookup_class=DniAfiliadoLookup,
        label="Dni (afiliado)",
        required=False,
        widget=AutoComboboxSelectWidget(DniAfiliadoLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )

    afiliado__cuit_empleador = AutoCompleteSelectField(
        lookup_class=CuitEmpleadorLookup,
        label="Cuit empleador",
        required=False,
        widget=AutoComboboxSelectWidget(CuitEmpleadorLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
