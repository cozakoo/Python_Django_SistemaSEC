from django import forms
from ..models import Pago_alumno
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from utils.constants import *
from ..forms.alumno_forms import AlumnoForm

class PagoAlumnoForms(forms.ModelForm):
    class Meta:
        model = Pago_alumno
        fields = '__all__'
        # exclude=['alumno']
        widgets ={
            'fecha_pago_alumno': forms.DateInput(attrs={'type':'date'})
            }
        labels = {
            'fecha_pago_alumno': "Fecha de pago",
        }

class FormularioPagoAlumno(forms.Form):
    def is_valid(self) -> bool:
        return super().is_valid()   and self.pagoAlumnoForm.is_valid() and self.alumnoForm.is_valid()

    def save(self, commit=False):
       # dictado = alumno
        #profesor = pagoAlumno
        alumno = self.alumnoForm.save(commit=False)
        pagoAlumno = self.pagoAlumnoForm.save(commit=False)

       
        alumno.save()
        pagoAlumno.alumno = alumno
        pagoAlumno.save()
        return alumno

    def __init__(self, initial=None, instance=None, *args, **kwargs):
            self.alumnoForm = AlumnoForm(initial=initial, instance=instance, *args, **kwargs)
            self.pagoAlumnoForm = PagoAlumnoForms(initial=initial, *args, **kwargs)
            #self.dictadoForm.fields['precio'].initial = curso.costo
            super().__init__(initial=initial,*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(
                Fieldset(
                    "",
                    'fecha_pago_alumno',
                    'monto',
                    ),

                
                Fieldset(
                    "Alumno",
                    'alumno',
                ),
                Submit('submit', 'Guardar', css_class='button white'),)

#FormularioPagoAlumno.base_fields.update(AlumnoForm.base_fields)
FormularioPagoAlumno.base_fields.update(PagoAlumnoForms.base_fields)