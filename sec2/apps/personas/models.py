from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from utils.choices import ESTADO_CIVIL, NACIONALIDADES
from utils.constants import *
from utils.funciones import validate_no_mayor_actual
from utils.regularexpressions import *
from datetime import date

class Persona(models.Model):
    dni = models.CharField(
        max_length=8,
        help_text='Sin puntos',
        validators=[
            numeric_validator,
            exact_length_8_validator,
        ],
    )
    cuil = models.CharField(
        max_length=11,
        help_text='Sin puntos y guiones',
        validators=[
            numeric_validator,
            exact_length_11_validator,
        ],
    )
    celular = models.CharField(
        max_length=10,
        help_text='Ejemplo: 1234567632',
        validators=[
            numeric_validator,
            exact_length_10_validator,
        ],
    )
    nacionalidad = models.CharField(
        max_length=2,
        choices=NACIONALIDADES,
        default="AR",
    )
    nombre = models.CharField(max_length=30, validators=[text_validator])
    apellido = models.CharField(max_length=30, validators=[text_validator])

    fecha_nacimiento = models.DateField(
        null=False,
        blank=False,
        validators=[validate_no_mayor_actual]
    )

    direccion = models.CharField(max_length=50, validators=[text_and_numeric_validator], help_text='Calle y numero')
    
    mail = models.EmailField(
        max_length=50,
        validators=[EmailValidator(message='Debe ser un correo válido.')],
        help_text='Debe ser un correo válido.'
    )
    
    estado_civil = models.PositiveSmallIntegerField(choices=ESTADO_CIVIL)

    es_afiliado = models.BooleanField(default=False)
    es_alumno = models.BooleanField(default=False)
    es_profesor = models.BooleanField(default=False)
    es_encargado = models.BooleanField(default=False)
    es_grupo_familiar = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return f"{self.apellido} {self.nombre}"
    
    @property
    def es_mayor_edad(self):
        # Calcula la edad comparando la fecha de nacimiento con la fecha actual
        edad = date.today().year - self.fecha_nacimiento.year - ((date.today().month, date.today().day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return edad >= 18
    
    def obtenerTipo(self):
        if self.es_afiliado:
            return 'Afiliado'
        elif self.es_grupo_familiar:
            return 'Familiar'
        elif self.es_profesor:
            return 'Profesor'
        elif self.es_alumno:
            return 'Alumno'
    
############## PATRON DE ROLES #####################################3
class Rol(models.Model):
    """
       TIPO PARA ROLES
        0: ROL DE ORIGEN
        1: AFILIADO
        2: GRUPO FAMILIAR
        3: ALUMNO
        4: PROFESOR
        5: ENCARGADO
    """
    TIPO = 0
    TIPOS = []
    persona = models.ForeignKey(Persona, related_name="roles", on_delete=models.CASCADE)
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)
    hasta = models.DateTimeField(null=True, blank=True)
    #se cambio de atributo para que se mueste en el chango
    desde = models.DateTimeField(null=True, blank=True)
    # desde = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.abrevituraTipoRol() } {self.persona.dni} {self.persona.nombre} {self.persona.apellido}"

    def abrevituraTipoRol(self):
        if self.tipo == 1: 
            return '(AF)'
        elif self.tipo == 2: 
            return '(F)'
        elif self.tipo == 3:
            return '(AL)'
        elif self.tipo == 4: 
            return '(P)'
        elif self.tipo == 5: 
            return '(E)'

    def obtenerTipo(self):
        if self.tipo == 1: 
            return 'Afiliado'
        elif self.tipo == 2: 
            return 'Familiar'
        elif self.tipo == 3:
            return 'Alumno'
        elif self.tipo == 4: 
            return 'Profesor'
        elif self.tipo == 5: 
            return 'Encargado'

    # def save(self, *args, **kwargs):
    #     if self.pk is None:
    #         self.tipo = self.__class__.TIPO
    #     super(Rol, self).save(*args, **kwargs)  # Corrección: llamada al método save de la clase base


    def related(self):
        return self.Rol != Rol and self or getattr(self, self.get_tipo_display())

    @classmethod
    def register(cls, Klass):
        cls.TIPOS.append((Klass.TIPO, Klass.__name__.lower()))
    
    def como(self, Klass):
        return self.roles.get(tipo=Klass.TIPO).related()

    def agregar_rol(self, rol):
        if not self.sos(rol.Rol):
            rol.persona = self
            rol.save()

    def roles_related(self):
        return [rol.related() for rol in self.roles.all()]

    def sos(self, Klass):
        return any([isinstance(rol, Klass) for rol in self.roles_related()])