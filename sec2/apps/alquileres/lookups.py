from __future__ import unicode_literals

from selectable.base import ModelLookup, LookupBase
from selectable.registry import registry

from unidecode import unidecode

from apps.alquileres.models import Encargado, Salon, Servicio
from apps.personas.models import Rol


class SalonLookup(ModelLookup):
    model = Salon
    search_fields = ('nombre__icontains', )

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(fechaBaja__isnull=True).order_by('nombre')
        return queryset
registry.register(SalonLookup)

class EncargadoLookup(ModelLookup):
    model = Encargado
    search_fields = ('persona__dni__icontains', 'persona__nombre__icontains','persona__apellido__icontains')
    
    def get_query(self, request, term):
        queryset = super().get_query(request, term)
        # Filtrar por aquellos encargados que no tienen fecha hasta
        queryset = queryset.filter(hasta__isnull=True)
        return queryset.order_by('persona__dni')[:5] 

    def format_item_display(self, item):
        # Utiliza unidecode para eliminar las tildes
        nombre_sin_tildes = unidecode(item.persona.nombre)
        apellido_sin_tildes = unidecode(item.persona.apellido)
        return f'{nombre_sin_tildes} {apellido_sin_tildes} ({item.persona.dni})'
registry.register(EncargadoLookup)


class DniEncargadoLookup(LookupBase):
    def get_query(self, request, term):
        queryset = self.get_queryset(term)  # Pasa el término de búsqueda a get_queryset
        # if term:
        return queryset

    def get_queryset(self, term):
        encargados = Encargado.objects.filter(persona__dni__icontains=term)[:3]  # Filtra por DNI y toma los primeros 3 resultados
        queryset = [
            {"id": encargado.persona.dni}
            for encargado in encargados
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

registry.register(DniEncargadoLookup)



class SalonNombreLookup(LookupBase):
    def get_query(self, request, term):
        queryset = self.get_queryset(term)  # Pasa el término de búsqueda a get_queryset
        # if term:
        return queryset

    def get_queryset(self, term):
        salones = Salon.objects.all()[:3]
        queryset = [
            {"id": salon.nombre}
            for salon in salones
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



class ServicioNombreLookup(LookupBase):
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

registry.register(ServicioNombreLookup)
