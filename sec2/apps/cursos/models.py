from django.db import models
from django.http import Http404, HttpResponse
from apps.personas.models import Rol
from utils.constants import *
from utils.choices import *
from utils.funciones import registrar_fuentes, validate_no_mayor_actual
from utils.regularexpressions import *
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

# ------------- ACTIVIDAD --------------------
class Actividad(models.Model):
    nombre = models.CharField(
        max_length=50,
        validators=[text_validator],  # Añade tu validador personalizado si es necesario
        help_text="Solo se permiten letras y espacios."
    )
    
    def __str__(self):
        return f"{self.nombre}"

# ------------- AULA --------------------
class Aula(models.Model):
    tipo = models.CharField(max_length=50, choices=TIPO_AULA, help_text="Tipo de aula")
    numero = models.PositiveIntegerField(help_text="Numero de aula")
    capacidad = models.PositiveIntegerField(help_text="Capacidad máxima")

    def clean(self):
        if self.numero <= 0:
            raise ValidationError({'numero': 'El número de aula debe ser mayor que 0.'})
        if self.capacidad <= 0:
            raise ValidationError({'cupo': 'La capacidad máxima del aula debe ser mayor que 0.'})

    def __str__(self):
        if self.tipo == 'normal':
            return 'Aula {}'.format(self.numero)
        return 'Computación {}'.format(self.numero)

#------------- LISTA DE ESPERA --------------------
class ListaEspera(models.Model):
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='inscritos_lista_espera')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    fechaInscripcion = models.DateTimeField(auto_now_add=True)
    
#------------- CURSO --------------------
class Curso(models.Model):
    class Meta:
        permissions = [("permission_gestion_curso", "Control total curso")]

    # ForeignKey
    actividad = models.ForeignKey(Actividad, on_delete=models.SET_NULL, blank=True, null=True)
    lista_espera = models.ManyToManyField(ListaEspera, blank=True, related_name='cursos_en_lista_espera')  # Change the related_name here

    area = models.PositiveSmallIntegerField(choices=AREAS, blank=True, null=True)
    requiere_certificado_medico = models.BooleanField(default=False)
    requiere_equipamiento_informatico = models.BooleanField(default=False)
    es_convenio = models.BooleanField(default=False)
    modulos_totales= models.PositiveIntegerField(help_text="Horas totales del curso")    
    nombre = models.CharField(
        max_length=50,
        validators=[text_and_numeric_validator],
        help_text="Solo se permiten letras, números y espacios, con o sin tildes."
    )
    descripcion = models.CharField(
        max_length=255,
        validators=[text_and_numeric_validator],  # Añade tu validador personalizado si es necesario
        help_text="Descripción del curso"
    )
    cupo_estimativo = models.PositiveIntegerField(
        help_text="Maximo por dictado",
        validators=[
            MinValueValidator(1, message="Valor mínimo permitido es 1."),
            MaxValueValidator(100, message="Valor máximo es 100."),
        ],
        null=True,
    )
    precio_total = models.DecimalField(
        help_text="Costo total del curso (Alumno)",
        max_digits=10,
        decimal_places=0,
        blank=True,   # Set this to True to make the field optional
        null=True,    # Also set null to True if you want to allow NULL values in the database
        default=0     # Set the default value to 0
    )
    precio_estimativo_profesor = models.DecimalField(
        help_text="Precio a pagar por profesor (estimado)",
        max_digits=10,
        decimal_places=0,
        blank=True,   # Set this to True to make the field optional
        null=True,    # Also set null to True if you want to allow NULL values in the database
        default=0     # Set the default value to 0
    )
    
    fechaBaja= models.DateField(
        null=True,
        blank=False,
    )

    
    def __str__(self):
        return f"{self.nombre}"
    
    def get_tipo_curso(self):
        if self.es_convenio:
            return 'convenio'
        elif self.requiere_certificado_medico:
            return 'actividad'
        else:
            return 'sec'

#------------- DICTADO --------------------
from django.utils.crypto import get_random_string

class Dictado(models.Model):
    # ForeignKey
    curso = models.ForeignKey(Curso, related_name="dictado_set", on_delete=models.CASCADE, null=True, blank=True)
    legajo = models.CharField(max_length=4, null=True, default=get_random_string(length=4, allowed_chars='1234567890'))
    modulos_por_clase= models.PositiveIntegerField(help_text="Horas por clase")
    asistencia_obligatoria = models.BooleanField(default=False)
    periodo_pago=models.PositiveSmallIntegerField(choices=PERIODO_PAGO)
    estado = models.PositiveSmallIntegerField(choices=ESTADO_DICTADO, default=1)
    fecha = models.DateTimeField(help_text="Seleccione la fecha de inicio")
    fecha_fin = models.DateTimeField(null=True,blank=True )
    cupo_real = models.PositiveIntegerField(
        help_text="Máximo inscriptos",
        validators=[
            MinValueValidator(1, message="Valor mínimo permitido es 1."),
            MaxValueValidator(100, message="Valor máximo es 100."),
        ]
    )
    descuento = models.PositiveIntegerField(
        help_text="Exclusivo para afiliados",
        validators=[
            MinValueValidator(0, message="El descuento no puede ser menor que 0."),
            MaxValueValidator(100, message="El descuento no puede ser mayor que 100."),
        ]
    )
    precio_real_profesor = models.DecimalField(
        help_text="Precio a pagar por profesor (real)",
        max_digits=10,
        decimal_places=0,
        blank=True,   # Set this to True to make the field optional
        null=True,    # Also set null to True if you want to allow NULL values in the database
        default=0     # Set the default value to 0
    )

#------------- HORARIO --------------------
from datetime import datetime, timedelta

class Horario(models.Model):
    # ForeignKey
    dictado = models.ForeignKey(Dictado, related_name="horarios", null=True, on_delete=models.CASCADE)
    
    dia_semana = models.PositiveSmallIntegerField(choices=DIAS_SEMANA_CHOICES)
    hora_inicio = models.TimeField(help_text="Ingrese la hora en formato de 24 horas (HH:MM)")
    hora_fin = models.TimeField(blank=True, null=True)
    #Utilizado para controlar que no se creen horarios antes del primer dictado creado
    es_primer_horario = models.BooleanField(default=False)  # Campo booleano con valor por defecto False

    def clean(self):
        if self.hora_inicio and self.dictado and self.dictado.modulos_por_clase:
            # Calcular la hora de fin al limpiar los datos del modelo
            hora_inicio_datetime = datetime.combine(datetime.today(), self.hora_inicio)
            tiempo_modulo = timedelta(hours=self.dictado.modulos_por_clase)
            hora_fin_datetime = hora_inicio_datetime + tiempo_modulo
            self.hora_fin = hora_fin_datetime.time()

    def calcular_hora_fin(self, hora_inicio, modulos_por_clase):
        # Calcular la hora de fin en cualquier otro lugar si es necesario
        if hora_inicio and modulos_por_clase:
            hora_inicio_datetime = datetime.combine(datetime.today(), hora_inicio)
            tiempo_modulo = timedelta(hours=modulos_por_clase)
            hora_fin_datetime = hora_inicio_datetime + tiempo_modulo
            return hora_fin_datetime.time()

# ------------- RESERVA --------------------
class Reserva(models.Model):
    # ForeignKey
    horario = models.ForeignKey(Horario, related_name="reservass", on_delete=models.CASCADE, null=True, blank=True)
    aula = models.ForeignKey(Aula, related_name="reservas", on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateField()

#------------- ALUMNO --------------------
class Alumno(Rol):
    # ForeignKey
    dictados = models.ManyToManyField(Dictado, related_name="alumnos", blank=True)
    # lista_espera = models.ManyToManyField('Dictado', related_name='alumnos_en_espera', blank=True)
    
    # Si realmente es un alumno o solo un interesado en algun curso
    es_potencial = models.BooleanField(default=True) 

    TIPO = ROL_TIPO_ALUMNO
    def agregar_dictado(self, dictado):
        if dictado.cupo > dictado.alumnos.count():
            self.dictados.add(dictado)
            return True
        else:
            # self.lista_espera.add(dictado)
            return False
    
    def esta_inscripto_o_en_espera(self, dictado):
        return dictado in self.dictados.all() 
    # or dictado in self.lista_espera.all()

    def esta_inscrito_en_dictado(self, dictado_pk):
        """
        Verifica si el alumno está inscrito en el dictado con la clave primaria dictado_pk.
        Devuelve True si está inscrito, False en caso contrario.
        """
        return self.dictados.filter(pk=dictado_pk).exists()

    def darDeBaja(self):
        self.hasta = date.today()
        self.persona.save()
        self.save()

Rol.register(Alumno)

#------------- PROFESOR --------------------
class Profesor(Rol):
    # ForeignKey
    dictados = models.ManyToManyField(Dictado, through = "Titular", related_name="profesores", blank=True)
    TIPO = ROL_TIPO_PROFESOR
    actividades = models.ManyToManyField(Actividad, blank=True)
    dictados_inscriptos = models.ManyToManyField(Dictado, related_name="profesores_dictados_inscriptos", blank=True)
    # lista_espera = models.ManyToManyField(Dictado, related_name='profesores_en_espera', blank=True)

    ejerce_desde= models.DateField(
        null=True,
        blank=False,
        validators=[validate_no_mayor_actual]
    )
    
    def esRolActivo(self):
        rol = get_object_or_404(Rol, persona__pk=self.persona.pk)
        if rol.hasta:
            return False
        else:
            return True

    def __str__(self):
        if self.persona_id and hasattr(self, 'persona'):
            return f"{self.persona.apellido} {self.persona.nombre}"
        else:
            return super().__str__()
    
    def dar_de_baja(self):
        self.hasta = date.today()
        self.save()

Rol.register(Profesor)

#------------- CLASE --------------------
class Clase(models.Model):
    reserva = models.ForeignKey(Reserva, related_name="clases", on_delete=models.CASCADE, null=True, blank=True)
    #para que se procesa a tomar la asistencia de la siguiente clase
    asistencia_tomada = models.BooleanField(default=False)
    
    # Agregar un campo para registrar la asistencia de diferentes roles
    asistencia = models.ManyToManyField(Rol, related_name="asistencias", blank=True)
    asistencia_profesor = models.ManyToManyField(Profesor, related_name="asistencias_titular", blank=True)

    def marcar_asistencia(self, rol):
        # Verificar que la asistencia no se haya tomado antes
        if not self.asistencia_tomada:
            self.asistencia.add(rol)
            return True
        else:
            return False

    def tomar_asistencia(self):
        # Marcar la asistencia para la clase
        self.asistencia_tomada = True
        self.save()
    
    def tiene_asistencia(self, inscrito):
        return inscrito in self.asistencia.all()

from django.shortcuts import get_object_or_404
# Luego, podrías usar este método en tu vista para marcar la asistencia de un alumno, profesor, etc.
def marcar_asistencia(request, clase_id, rol_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    rol = get_object_or_404(Rol, pk=rol_id)

    if clase.marcar_asistencia(rol):
        return HttpResponse("Asistencia marcada correctamente.")
    else:
        return HttpResponse("Error: La asistencia ya ha sido tomada.")

#------------- TITULAR --------------------
class Titular(models.Model):
    # ForeignKey
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    dictado= models.ForeignKey(Dictado, on_delete=models.CASCADE)

from io import BytesIO
import io
from reportlab.pdfgen import canvas
from django.http import FileResponse

class PagoProfesor(models.Model):
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='pagos_profesor')
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    pre_factura = models.FileField(upload_to='prefacturas/', null=True, blank=True)

    def generarPreFactura(self):
        buffer = self.generarPdf()
        filename = "Comprobante-pre-factura.pdf"
        self.pre_factura.save(filename, buffer)
    
    def descargarPreFactura(self):
        # Llamar al método generarPreFactura para asegurarse de que el archivo esté generado
        self.generarPreFactura()

        # Abrir el archivo y enviarlo como una respuesta HTTP para descargarlo automáticamente
        try:
            with open(self.pre_factura.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="Comprobante-pre-factura.pdf"'
                return response
        except FileNotFoundError:
            raise Http404("El archivo no existe")
    
    def generarPdf(self):
        registrar_fuentes()
        
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        # Establecer propiedades del documento
        pdf.setTitle("Comprobante de pago")
        pdf.setSubject("Pre-factura de pago")

        titulo = "Comprobante de pago"
        self.establecer_titulo(pdf, titulo)
        self.agregarDetalleRol(pdf)
        self.agregarPago(pdf)
        self.agregarDetallesPago(pdf)

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer

    def agregarPago(self, pdf):
        pdf.setFont("Calibri", 11)
        pdf.drawString(100, 550, f'Fecha: {self.fecha.strftime("%Y/%m/%d")}')

    def agregarDetallesPago(self, pdf):
        # Get details for the payment
        detalles_pago = self.detalles_pago.all()
        # Define table data
        data = [['Dictado',  'Tot clases','clases asist', '% Asistencia', 'Total']]

        for detalle in detalles_pago:
            data.append([
                str(detalle.dictado.curso.nombre),
                f'{detalle.total_clases}',
                f'{detalle.clases_asistidas}',
                f'{detalle.porcentaje_asistencia}%',
                str(detalle.precioFinal),
            ])
        
        # Add a row for total payment
        total_row = [''] * len(data[0])  # Create an empty row with the same number of columns
        total_row[-2] = 'Total'  # Set 'Total' in the second to last column
        total_row[-1] = f'${self.total}'  # Set total payment amount in the last column
        data.append(total_row)

        # Define table style
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # Align all columns to the right
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        # Create table and apply style
        detalles_table = Table(data)
        detalles_table.setStyle(style)

        # Draw table on PDF
        detalles_table.wrapOn(pdf, 400, 450)
        detalles_table.drawOn(pdf, 50, 450)  

    def establecer_titulo(self, pdf, titulo):
        pdf.setFont('Times-Bold', 14)
        pdf.drawCentredString(300, 745, "Sindicato de Empleado de Comercio 2")
        pdf.drawCentredString(300, 720, titulo)

    def agregarDetalleRol(self, pdf):
        pdf.setFont("Calibri", 11)
        
        pdf.drawRightString(295, 695, f'DNI:')
        pdf.drawRightString(295, 675, f'Nombre:')
        pdf.drawRightString(295, 655, f'Mail:')
        pdf.drawRightString(295, 635, f'Celular:')
        pdf.drawString(300, 695, f'{self.profesor.persona.dni}')
        pdf.drawString(300, 675, f'{self.profesor} {self.profesor}')
        pdf.drawString(300, 655, f'{self.profesor.persona.mail}')
        pdf.drawString(300, 635, f'{self.profesor.persona.celular}')


class DetallePagoProfesor(models.Model):
    pago_profesor = models.ForeignKey(PagoProfesor, on_delete=models.CASCADE, related_name='detalles_pago')
    dictado = models.ForeignKey(Dictado, on_delete=models.CASCADE)
    total_clases = models.IntegerField()
    clases_asistidas = models.IntegerField()
    porcentaje_asistencia = models.IntegerField()
    precioFinal = models.DecimalField(max_digits=10, decimal_places=2, null=True)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle

class PagoAlumno(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='pagos_rol', null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, validators=[MinValueValidator(0, 'El monto debe ser un valor positivo.')])
    fecha = models.DateTimeField(auto_now_add=True)
    pre_factura = models.FileField(upload_to='prefacturas/', null=True, blank=True)
    
    def generarPreFactura(self):
        buffer = self.generarPdf()
        filename = "Comprobante-pre-factura.pdf"
        self.pre_factura.save(filename, buffer)
    
    def descargarPreFactura(self):
        # Llamar al método generarPreFactura para asegurarse de que el archivo esté generado
        self.generarPreFactura()

        # Abrir el archivo y enviarlo como una respuesta HTTP para descargarlo automáticamente
        try:
            with open(self.pre_factura.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="Comprobante-pre-factura.pdf"'
                return response
        except FileNotFoundError:
            raise Http404("El archivo no existe")
    
    def generarPdf(self):
        registrar_fuentes()
        
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        # Establecer propiedades del documento
        pdf.setTitle("Comprobante de pago")
        pdf.setSubject("Pre-factura de pago")
        
        titulo = "Comprobante de pago del dictado"
        self.establecer_titulo(pdf, titulo)
        self.agregarDetalleRol(pdf)
        self.agregarPago(pdf)
        self.agregarDetallesPago(pdf) 

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer

    def agregarPago(self, pdf):
        pdf.setFont("Calibri", 11)
        pdf.drawString(100, 550, f'Fecha: {self.fecha.strftime("%Y/%m/%d")}')

    def agregarDetallesPago(self, pdf):
        # Get details for the payment
        detalles_pago = self.detalles_pago_alumno.all()
        # Define table data
        data = [['Dictado',  'Precio','Desc', 'Precio (Desc)', 'Periodo', 'Cant',   'Total']]

        for detalle in detalles_pago:
            data.append([
                str(detalle.dictado.curso.nombre),
                f'${detalle.precioFinal}',
                f'{detalle.descuento}%',
                f'${detalle.precioConDescuento}',
                detalle.get_periodo_pago_display(),
                str(detalle.cantidad),
                f'${detalle.total}'
            ])
        
        # Add a row for total payment
        total_row = [''] * len(data[0])  # Create an empty row with the same number of columns
        total_row[-2] = 'Total'  # Set 'Total' in the second to last column
        total_row[-1] = f'${self.total}'  # Set total payment amount in the last column
        data.append(total_row)

        # Define table style
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # Align all columns to the right
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        # Create table and apply style
        detalles_table = Table(data)
        detalles_table.setStyle(style)

        # Draw table on PDF
        detalles_table.wrapOn(pdf, 400, 450)
        detalles_table.drawOn(pdf, 50, 450)  

    def agregarDetalleRol(self, pdf):
        pdf.setFont("Calibri", 11)
        
        pdf.drawRightString(295, 695, f'DNI:')
        pdf.drawRightString(295, 675, f'Nombre:')
        pdf.drawRightString(295, 655, f'Mail:')
        pdf.drawRightString(295, 635, f'Celular:')
        pdf.drawString(300, 695, f'{self.rol.persona.dni}')
        pdf.drawString(300, 675, f'{self.rol.persona.nombre} {self.rol.persona.apellido}')
        pdf.drawString(300, 655, f'{self.rol.persona.mail}')
        pdf.drawString(300, 635, f'{self.rol.persona.celular}')

    def establecer_titulo(self, pdf, titulo):
        pdf.setFont('Times-Bold', 14)
        pdf.drawCentredString(300, 770, "Sindicato de Empleado de Comercio 2")
        pdf.drawCentredString(300, 745, titulo)

class DetallePagoAlumno(models.Model):
    pago_alumno = models.ForeignKey(PagoAlumno, on_delete=models.CASCADE, related_name='detalles_pago_alumno')
    dictado = models.ForeignKey(Dictado, on_delete=models.CASCADE)
    periodo_pago=models.PositiveSmallIntegerField(choices=PERIODO_PAGO)
    cantidad = models.IntegerField()
    descuento = models.IntegerField()
    tipo_pago = models.CharField(max_length=255)
    precioFinal = models.DecimalField(max_digits=10, decimal_places=2, null=True, validators=[MinValueValidator(0, 'El monto debe ser un valor positivo.')])
    precioConDescuento = models.DecimalField(max_digits=10, decimal_places=2, null=True, validators=[MinValueValidator(0, 'El monto debe ser un valor positivo.')])
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, validators=[MinValueValidator(0, 'El monto debe ser un valor positivo.')])

