import datetime
from unittest.util import _MAX_LENGTH
from django.db import models
from apps.personas.models import *
from apps.afiliados.models import *
from utils.choices import LOCALIDADES_CHUBUT
from apps.personas.models import Rol, Persona
from django.db.models import Count
from django import forms
from datetime import datetime

class Servicio (models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.nombre}"
    
class Encargado (Rol):
    TIPO=ROL_TIPO_ENCARGADO
    dictados = models.ManyToManyField(Dictado, related_name="encargados", blank=True)

    def __str__(self):
        return f"{self.persona.dni} | {self.persona.nombre} {self.persona.apellido}"
Rol.register(Encargado)

class Salon(models.Model):
    TIPO_SALON=[
        (1,'Polideportivo'),
        (2,'Multiuso')
    ]
    nombre = models.CharField(max_length=30)
    localidad= models.CharField(max_length =25,choices = LOCALIDADES_CHUBUT)
    direccion=models.CharField(max_length=50)
    capacidad=models.PositiveIntegerField()
    encargado=models.ForeignKey(Encargado, related_name="salon", on_delete=models.CASCADE)
    precio=models.DecimalField(help_text="costo del alquiler", max_digits=10, decimal_places=2)
    fechaBaja= models.DateField(null=True,blank=False)
    tipo_salon = models.PositiveSmallIntegerField(choices=TIPO_SALON)
    servicios=models.ManyToManyField(Servicio, blank=True) 
    
    def __str__(self):
        return f"{self.nombre} | Capacidad: {self.capacidad} personas"
    

class Alquiler(models.Model):
    class Meta:
         permissions = [("permission_gestion_alquiler", "Control total alquiler")]

         

    ESTADOS = (
        (1, 'Confirmado'), # esta pactado la fecha 
        (2, 'En curso'),  #es la fecha actual
        (3, 'Finalizado'), # se reaizo el alquiler
        (4, 'Cancelado'), # se cancelo antes de que se realice
    )

    TURNOS=[

        ('Mañana','Mañana'),
        ('Noche','Noche')
    ]
    cambio_inquilino = models.BooleanField(default=False)  # Campo booleano para indicar si se realizó un cambio de inquilino
    estado = models.IntegerField(choices=ESTADOS, default=1)
    afiliado=models.ForeignKey(Afiliado, related_name="alquileres", on_delete=models.CASCADE)
    salon=models.ForeignKey(Salon, related_name="alquileres", on_delete=models.CASCADE)
    fecha_solicitud=models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_alquiler=models.DateTimeField(null=True, blank=True) 
    turno=models.CharField(max_length=50, choices=TURNOS) #verificar bien la forma de los turnos
    seguro=models.DecimalField(help_text="costo del alquiler", max_digits=10, decimal_places=2)
    lista_espera=models.ManyToManyField(Afiliado, blank=True)
    fechaBaja= models.DateField(null=True,blank=False)
    #crear lista de espera para agregar afiliado interesado que solamente mostrara para el afiliado que esta en espera, el sistea no se encarga de la actulizacion del cliente de manera automatica a la hora actulizar el cliente que contrata el salon
    #servicios[1..n] no se detallan los servicios "extras" que ofrece el sindicato porque solamente hace de nexo entre la empresa que lo ofrece y el afiliado

    def __str__(self):
        return f"{self.fecha_alquiler, self.turno, self.afiliado.persona, self.salon}"
    
    def verificar_existencia_alquiler(self, salon, fecha_alquiler, turno):
        # Verificar si existe algún alquiler que cumple con las condiciones dadas
        alquiler_existente = Alquiler.objects.filter(salon=salon, fecha_alquiler=fecha_alquiler, turno=turno, estado=1).exists()
       # Devolver True si existe al menos un alquiler que cumple con las condiciones
        return alquiler_existente

    def fecha_valida(fecha):
            #Verifica que la fecha sea mayor a la de hoy
            hoy = datetime.today()
                
            if fecha.date() > hoy.date():
                return True
            else:
                return False
            
            
class Pago_alquiler(models.Model):
    alquiler=models.ForeignKey(Alquiler, related_name="pagos", on_delete=models.CASCADE)
    fecha_pago=models.DateTimeField(auto_now_add=True, null=True, blank=True)
    FORMA_PAGO=[
        ('total','Total'),
        ('cuota','Cuota')
    ]
    forma_pago = models.CharField(max_length=30, choices=FORMA_PAGO)
    #agregar las dos formas de pago total(no importa si es contado o tarjeta) o cuota (no  se realiza en el sistema la forma de pago y como se actualiza)
    #ver si el sistema entrega comprobante de pago

    def alquileres_sin_pago():
    # Obtener todos los alquileres que no tienen ningún pago asociado
        alquileres_sin_pagos = Alquiler.objects.annotate(num_pagos=Count('pagos')).filter(num_pagos=0)
        return alquileres_sin_pagos