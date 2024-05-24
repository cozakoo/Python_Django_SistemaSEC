from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from utils.constants import *

from django.core.validators import RegexValidator

# Expresiones regulares y mensajes genéricos
DIGITS_REGEX = r'^\d+$'
EXACT_LENGTH_8_REGEX = r'^\d{8}$'
EXACT_LENGTH_10_REGEX = r'^\d{10}$'
EXACT_LENGTH_11_REGEX = r'^\d{11}$'

DIGITS_ONLY_MESSAGE = 'Debe contener solo dígitos numéricos.'
EXACT_LENGTH_8_MESSAGE = 'Debe tener exactamente 8 dígitos.'
EXACT_LENGTH_10_MESSAGE = 'Debe tener exactamente 10 dígitos.'
EXACT_LENGTH_11_MESSAGE = 'Debe tener exactamente 11 dígitos.'

# Validador genérico para números y longitud específica
numeric_validator = RegexValidator(
    regex=DIGITS_REGEX,
    message=DIGITS_ONLY_MESSAGE,
    code='invalid_numeric'
)

exact_length_8_validator = RegexValidator(
    regex=EXACT_LENGTH_8_REGEX,
    message=EXACT_LENGTH_8_MESSAGE,
    code='invalid_length_8'
)
exact_length_10_validator = RegexValidator(
    regex=EXACT_LENGTH_10_REGEX,
    message=EXACT_LENGTH_10_MESSAGE,
    code='invalid_length_8'
)

exact_length_11_validator = RegexValidator(
    regex=EXACT_LENGTH_11_REGEX,
    message=EXACT_LENGTH_11_MESSAGE,
    code='invalid_length_11'
)



numeric_validator = RegexValidator(
        regex=r'^\d+$',
        message=f'Debe contener solo dígitos numéricos.',
        code='invalid_numeric'
    )

text_validator = RegexValidator(
    regex=r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s.]+$',
    message=f'Debe contener letras, espacios',
    code='invalid_text'
)

text_and_numeric_validator = RegexValidator(
    regex=r'^[A-Za-z0-9\sñÑáéíóúÁÉÍÓÚ]+$',
    message='Solo se permiten letras, números y espacios, con o sin tildes.',
    code='invalid_text'
)

def validate_positive_decimal(value):
    if value < 0:
        raise ValidationError(f'El sueldo no puede ser un valor negativo.')

def telefono_argentino_validator(value):
    if not value:
        return  # Permite valores vacíos, ya que eso debería ser manejado por otro validador si es necesario.

    # Acepta los formatos +549XXXXXXXXX, 0XX-XXXXXXXX, 15XXXXXXXXX.
    pattern = r'^(\+?549\d{9}|0\d{2}-\d{8}|15\d{8})$'
    if not RegexValidator(pattern)(value):
        raise ValidationError('Número de teléfono no válido para Argentina. Utilice el formato +549XXXXXXXXX, 0XX-XXXXXXXX o 15XXXXXXXXX.')

# Define una función para validar si el valor es un número
def is_numeric(value):
    return value.isnumeric()
