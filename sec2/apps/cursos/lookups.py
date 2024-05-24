from __future__ import unicode_literals

from selectable.base import ModelLookup, LookupBase
from apps.alquileres.models import Salon, Servicio
from apps.cursos.models import Actividad, Alumno, Curso, Profesor

from selectable.registry import registry


class CursoLookup(ModelLookup):
    model = Curso
    search_fields = ('nombre__icontains', )

    def get_query(self, request, term):
        queryset = super().get_query(request, term)
        return queryset.order_by('nombre')[:5] 

registry.register(CursoLookup)

class ActividadNombreLookup(LookupBase):
    def get_query(self, request, term):
        queryset = self.get_queryset(term)  # Pasa el término de búsqueda a get_queryset
        # if term:
        return queryset

    def get_queryset(self, term):
        actividades = Actividad.objects.filter(nombre__icontains=term)[:3]  # Filtra por DNI y toma los primeros 3 resultados
        queryset = [
            {"id": actividad.nombre}
            for actividad in actividades
        ]
        return queryset
    
    def get_item_value(self, item):
        return item.get("id", "")

    
    def get_item_id(self, item):
        return item.get("id", "")

    
    def get_item_label(self, item):
        return item.get("id", "")
    
    def get_item_value(self, item):
        if isinstance(item, dict):  # Verifica si item es un diccionario
            return item.get("id", "")  # Utiliza .get() para obtener el valor de "id"
        else:
            return ""  # Si item no es un diccionario, devuelve un valor predeterminado o maneja el caso según sea necesario

registry.register(ActividadNombreLookup)


class ActividadLookup(ModelLookup):
    model = Actividad
    search_fields = ('nombre__icontains', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

registry.register(ActividadLookup)


class PagoAlumnoLookup(ModelLookup):
    model = Actividad
    search_fields = ('nombre__icontains', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

registry.register(PagoAlumnoLookup)


class DniAlumnoLookup(LookupBase):
    def get_query(self, request, term):
        queryset = self.get_queryset(term)  # Pasa el término de búsqueda a get_queryset
        # if term:
        return queryset

    def get_queryset(self, term):
        alumnos = Alumno.objects.filter(persona__dni__icontains=term)[:3]  # Filtra por DNI y toma los primeros 3 resultados
        queryset = [
            {"id": alumno.persona.dni}
            for alumno in alumnos
        ]
        return queryset
    
    def get_item_value(self, item):
        return item.get("id", "")

    
    def get_item_id(self, item):
        return item.get("id", "")

    
    def get_item_label(self, item):
        return item.get("id", "")
    
    def get_item_value(self, item):
        if isinstance(item, dict):  # Verifica si item es un diccionario
            return item.get("id", "")  # Utiliza .get() para obtener el valor de "id"
        else:
            return ""  # Si item no es un diccionario, devuelve un valor predeterminado o maneja el caso según sea necesario

registry.register(DniAlumnoLookup)

class ApellidoAlumnoLookup(LookupBase):
    def get_query(self, request, term):
        queryset = self.get_queryset(term)  # Pasa el término de búsqueda a get_queryset
        # if term:
        return queryset

    def get_queryset(self, term):
        alumnos = Alumno.objects.filter(persona__apellido__icontains=term)[:3]  # Filtra por DNI y toma los primeros 3 resultados
        queryset = [
            {"id": alumno.persona.apellido}
            for alumno in alumnos
        ]
        return queryset
    
    def get_item_value(self, item):
        return item.get("id", "")

    
    def get_item_id(self, item):
        return item.get("id", "")

    
    def get_item_label(self, item):
        return item.get("id", "")
    
    def get_item_value(self, item):
        if isinstance(item, dict):  # Verifica si item es un diccionario
            return item.get("id", "")  # Utiliza .get() para obtener el valor de "id"
        else:
            return ""  # Si item no es un diccionario, devuelve un valor predeterminado o maneja el caso según sea necesario

registry.register(ApellidoAlumnoLookup)


class ProfesorDniLookup(LookupBase):
    def get_query(self, request, term):
        queryset = self.get_queryset(term)  # Pasa el término de búsqueda a get_queryset
        # if term:
        return queryset

    def get_queryset(self, term):
        profesores = Profesor.objects.filter(persona__dni__icontains=term)[:3]  # Filtra por DNI y toma los primeros 3 resultados
        queryset = [
            {"id": profesor.persona.dni}
            for profesor in profesores
        ]
        return queryset
    
    def get_item_value(self, item):
        return item.get("id", "")

    
    def get_item_id(self, item):
        return item.get("id", "")

    
    def get_item_label(self, item):
        return item.get("id", "")
    
    def get_item_value(self, item):
        if isinstance(item, dict):  # Verifica si item es un diccionario
            return item.get("id", "")  # Utiliza .get() para obtener el valor de "id"
        else:
            return ""  # Si item no es un diccionario, devuelve un valor predeterminado o maneja el caso según sea necesario

registry.register(ProfesorDniLookup)



class ProfesorCapacitadoDniLookup(LookupBase):
    def get_query(self, request, term, actividad_curso):  # Agregar actividad_curso como un argumento adicional
        queryset = self.get_queryset(term, actividad_curso)  # Pasar actividad_curso a get_queryset
        return queryset

    def get_queryset(self, term, actividad_curso):  # Agregar actividad_curso como un parámetro adicional
        profesores = Profesor.objects.filter(persona__dni__icontains=term, actividades=actividad_curso)[:3]  # Filtrar por DNI y actividad_curso
        queryset = [
            {
                "id": profesor.id,
                "dni": profesor.persona.dni,
                "apellido": profesor.persona.apellido,
                "nombre": profesor.persona.nombre
             }
            for profesor in profesores
        ]
        return queryset
    
    def get_item_value(self, item):
        return item.get("id", "")

    
    def get_item_id(self, item):
        return item.get("id", "")

    
    def get_item_label(self, item):
        return item.get("id", "")
    
    def get_item_value(self, item):
        if isinstance(item, dict):  # Verifica si item es un diccionario
            return item.get("id", "")  # Utiliza .get() para obtener el valor de "id"
        else:
            return ""  # Si item no es un diccionario, devuelve un valor predeterminado o maneja el caso según sea necesario

registry.register(ProfesorCapacitadoDniLookup)




class SalonNombreLookup(LookupBase):
    def get_query(self, request, term):
        queryset = self.get_queryset(term)  # Pasa el término de búsqueda a get_queryset
        # if term:
        return queryset

    def get_queryset(self, term):
        servicios = Servicio.objects.filter(nombre__icontains=term)[:3]  # Filtra por DNI y toma los primeros 3 resultados
        queryset = [
            {"id": servicio.nombre}
            for servicio in servicios
        ]
        return queryset
    
    def get_item_value(self, item):
        return item.get("id", "")

    
    def get_item_id(self, item):
        return item.get("id", "")

    
    def get_item_label(self, item):
        return item.get("id", "")
    
    def get_item_value(self, item):
        if isinstance(item, dict):  # Verifica si item es un diccionario
            return item.get("id", "")  # Utiliza .get() para obtener el valor de "id"
        else:
            return ""  # Si item no es un diccionario, devuelve un valor predeterminado o maneja el caso según sea necesario

registry.register(SalonNombreLookup)