from django.utils import timezone
from django.forms import ValidationError
from django.contrib import messages
from .choices import MONTH_CHOICES

from utils.constants import ICON_CHECK, ICON_ERROR, ICON_TRIANGLE

# ------------- FUNCIONES PARA MENSAJES ------------------
def mensaje_error(request, message):
    messages.error(request, f'{ICON_ERROR} {message}')

def mensaje_exito(request, message):
    messages.success(request, f'{ICON_CHECK} {message}')

def mensaje_advertencia(request, message):
    messages.warning(request, f'{ICON_TRIANGLE} {message}')
#-----------------------------------------------------------

def validate_no_mayor_actual(value):
    if value > timezone.now().date():
        raise ValidationError('La fecha no puede ser en el futuro.')



def handle_existing_person(self, form):
    dni = form.cleaned_data["dni"]
    messages.error(self.request, f'{ICON_ERROR} ERROR: Ya existe una persona registrada en el sistema con el mismo DNI.')
    return self.render_to_response(self.get_context_data(form=form))

# -------------------- PDF -----------------
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def registrar_fuentes():
    pdfmetrics.registerFont(TTFont('Calibri', 'calibri.ttf'))
    pdfmetrics.registerFont(TTFont('TituloFont', 'times.ttf'))
    pdfmetrics.registerFont(TTFont('Times-Italic', 'timesi.ttf'))
    pdfmetrics.registerFont(TTFont('Times-Bold', 'timesbd.ttf'))


#-------------- FILTROS ------------------------------

def filter_by_persona_dni(queryset, dni):
        if dni:
            return queryset.filter(persona__dni__icontains=dni)
        return queryset

def filter_by_cuit_empleador(queryset, cuit_empleador):
        if cuit_empleador:
            return queryset.filter(cuit_empleador=cuit_empleador)
        return queryset

def filter_by_estado(queryset, estado):
        if estado:
            return queryset.filter(estado__in=estado)
        return queryset

def obtenerMes(number):
    month_name = next(name for num, name in MONTH_CHOICES if num == number)
    return  month_name 