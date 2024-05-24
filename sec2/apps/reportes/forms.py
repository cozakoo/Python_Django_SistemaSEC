from datetime import timezone
from datetime import datetime
from django import forms
from django.core.validators import RegexValidator
from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget

from apps.cursos.lookups import CursoLookup


def obtenerAnio():
    return str(datetime.today().year)


class CursosListFilterForm(forms.Form):
    

    anio = forms.CharField(empty_value=obtenerAnio(), max_length=4)

    curso_nombre = AutoCompleteSelectField(

        lookup_class=CursoLookup,

        required=False,

        widget=AutoComboboxSelectWidget(CursoLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
  


    def get_query(self, request, term):

        queryset = super().get_query(request, term)

        return queryset.order_by('curso__nombre')[:5] 
    

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


class YearcomparacionForm(forms.Form):
    year1 = forms.CharField(
        max_length=4,
        validators=[RegexValidator(regex='^[0-9]{4}$', message='ingrese un año valdido')],
        widget=forms.TextInput(attrs={'maxlength': 4, 'class': 'form-control', 'placeholder': 'Ingrese 1° año'})
    )
    year2 = forms.CharField(
        max_length=4,
        validators=[RegexValidator(regex='^[0-9]{4}$', message='Ingrese un año válido.')],
        widget=forms.TextInput(attrs={'maxlength': 4, 'class': 'form-control', 'placeholder': 'Ingrese 2° año'})
    )

    def clean(self):
        cleaned_data = super().clean()
        year1 = cleaned_data.get('year1')
        year2 = cleaned_data.get('year2')
        if year1 and year2:
            if year1 == year2:
                raise forms.ValidationError("Los años deben ser distintos.")
        return cleaned_data

class YearForm(forms.Form):
    year = forms.CharField(
        max_length=4,
        validators=[RegexValidator(regex='^[0-9]{4}$', message='Ingrese un año válido.')],
        widget=forms.TextInput(attrs={'maxlength': 4})
       )
