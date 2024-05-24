from django.contrib import admin

from .models import Persona

# Register your models here.
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('dni', 'apellido', 'nombre', 'fecha_nacimiento', 'es_alumno')
    list_filter = ('dni','apellido')
    ordering = ('dni', 'apellido')

admin.site.register(Persona, PersonaAdmin)


