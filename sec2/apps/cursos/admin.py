from django.contrib import admin

from apps.cursos.forms.curso_forms import ListaEsperaAdminForm
from .models import Actividad, Alumno, Clase, Curso, Aula, DetallePagoAlumno, DetallePagoProfesor, Dictado, Horario, ListaEspera, PagoAlumno, PagoProfesor, Reserva, Profesor, Titular

class AulaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'capacidad')
admin.site.register(Aula, AulaAdmin)

class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
admin.site.register(Curso, CursoAdmin)

class DictadoAdmin(admin.ModelAdmin):
    list_display = ('fecha',)
admin.site.register(Dictado, DictadoAdmin)

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('fecha','aula', 'horario')
admin.site.register(Reserva, ReservaAdmin)

class HorarioAdmin(admin.ModelAdmin):
    list_display = ('hora_inicio',)
admin.site.register(Horario, HorarioAdmin)

class ClaseAdmin(admin.ModelAdmin):
    list_display = ('reserva',)
admin.site.register(Clase, ClaseAdmin)

class ActividadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
admin.site.register(Actividad, ActividadAdmin)

admin.site.register(Alumno)
admin.site.register(Profesor)
admin.site.register(Titular)
admin.site.register(PagoProfesor)
admin.site.register(DetallePagoProfesor)
admin.site.register(PagoAlumno)
admin.site.register(DetallePagoAlumno)

class ListaEsperaAdmin(admin.ModelAdmin):
    form = ListaEsperaAdminForm
    list_display = ('curso', 'rol', 'fechaInscripcion')
    # Agrega otras configuraciones del modelo ListaEsperaAdmin según tus necesidades

# Registra el modelo ListaEspera con la configuración personalizada en el panel de administración
admin.site.register(ListaEspera, ListaEsperaAdmin)