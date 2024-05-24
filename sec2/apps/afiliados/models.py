from django.db import models
from apps.cursos.models import Dictado
from apps.personas.models import Rol
from utils.choices import AFILIADO_ESTADO, LOCALIDADES_CHUBUT, TIPOS_RELACION_FAMILIAR
from utils.constants import *
from utils.funciones import validate_no_mayor_actual
from utils.regularexpressions import *
from datetime import date
from django.utils import timezone

# -------------------- FAMILIAR ------------------
class Familiar(Rol):
    TIPO = ROL_TIPO_FAMILIAR  # Define un valor único para el tipo de rol de Familiar
    activo = models.BooleanField(default=False)  # Agregamos el campo "activo" con valor predeterminado True
    dictados = models.ManyToManyField(Dictado, related_name="familiares", blank=True)
    # lista_espera = models.ManyToManyField(Dictado, related_name='familiares_en_espera', blank=True)
    
    def __str__(self):
        return f"Activo: {self.activo}"

Rol.register(Familiar)

# -------------------- AFILIADO ------------------
class Afiliado(Rol):
    class Meta:
        permissions = [("permission_gestion_afiliado", "Control total afiliado")]

    #Utilizado para Rol
    TIPO = ROL_TIPO_AFILIADO
    estado = models.PositiveSmallIntegerField(choices=AFILIADO_ESTADO, default=1)
    razon_social = models.CharField(max_length=50, validators=[text_and_numeric_validator])
    categoria_laboral = models.CharField(max_length=50, validators=[text_and_numeric_validator])
    rama = models.CharField(max_length=50, validators=[text_and_numeric_validator])
    sueldo = models.IntegerField(validators=[MinValueValidator(0, 'El sueldo debe ser un valor positivo.')])
    horaJornada = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    cuit_empleador = models.CharField(max_length=11, validators=[numeric_validator], help_text='Cuit sin puntos y guiones. Ej: 01234567899')
    domicilio_empresa = models.CharField(max_length=100, validators=[text_and_numeric_validator], help_text='Calle y numero')

    fechaAfiliacion= models.DateField(
        null=True,
        blank=False,
        validators=[validate_no_mayor_actual]
    )
    fechaIngresoTrabajo = models.DateField(
        null=False,
        blank=False,
        validators=[validate_no_mayor_actual]
    )
    localidad_empresa = models.CharField(
        max_length=30,
        choices=LOCALIDADES_CHUBUT,
        default="TRELEW",
    )

    dictados = models.ManyToManyField(Dictado, related_name="afiliados", blank=True)
    # lista_espera = models.ManyToManyField(Dictado, related_name='afiliados_en_espera', blank=True)
    familia = models.ManyToManyField(Familiar, through='RelacionFamiliar', blank=True)
    
    def __str__(self):
        return f"{self.persona.dni} {self.persona.apellido} {self.persona.nombre}. Estado: {self.get_estado_display()}"
    
    def __strextra__(self):
        # Define your new string representation here
        return f"{self.persona.dni} | {self.persona}"
    
    def tiene_esposo(self):
        esposo_existente = self.familia.filter(relacionfamiliar__tipo_relacion=1).exists()
        return esposo_existente
    
    """una vez activado al afiliado pondra a los familiares en estado de activo"""
    def activar_familiares(self):
        familiares = self.familia.all()
        for familiar in familiares:
            familiar.activo = True
            familiar.save()
    
    def dar_de_baja_familiares(self):
        familiares = self.familia.all()
        for familiar in familiares:
            familiar.activo = False
            familiar.hasta = timezone.now()
            familiar.save()

    def valorCuota(self):
        # Calcular el 1% del sueldo
        return self.sueldo * 0.01
    
    def actualizarSueldo(self, monto):
        self.sueldo = monto * 100
        self.save()

    def afiliar(self):
        self.fechaAfiliacion = date.today()
        # self.desde = fechaAfiliacion
        self.estado = 2
        self.persona.es_afiliado = True
        self.activar_familiares()
        self.persona.save()
        self.save()

    def desafiliar(self):
        self.hasta = date.today()
        self.estado = 3
        self.persona.es_afiliado = False
        self.dar_de_baja_familiares()
        self.persona.save()
        self.save()

Rol.register(Afiliado)

# -------------------- RELACION FAMILIAR-AFILIADO ------------------
class RelacionFamiliar(models.Model):
    afiliado = models.ForeignKey(Afiliado, on_delete=models.CASCADE)
    familiar = models.ForeignKey(Familiar, on_delete=models.CASCADE)
    tipo_relacion = models.PositiveSmallIntegerField(choices=TIPOS_RELACION_FAMILIAR)

    def __str__(self):
        return f"Relación: {self.get_tipo_relacion_display()}"

# -------------------- PAGO DE CUOTA ------------------
class PagoCuota(models.Model):
    afiliado = models.ForeignKey(Afiliado, on_delete=models.CASCADE, related_name='pagos_cuotas')
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0, 'El monto debe ser un valor positivo.')])
    pdf_transferencia = models.FileField(upload_to='transferencias/', null=True, blank=True)
    fecha_pago = models.DateField(default=timezone.now)
