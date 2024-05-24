from django.contrib import admin

from apps.alquileres.models import Alquiler, Encargado, Pago_alquiler, Salon, Servicio

admin.site.register(Encargado)
admin.site.register(Servicio)
admin.site.register(Salon)
admin.site.register(Alquiler)
admin.site.register(Pago_alquiler)