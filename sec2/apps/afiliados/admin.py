from django.contrib import admin
from .models import Afiliado, Familiar, PagoCuota, RelacionFamiliar
from apps.personas.models import Rol

class AfiliadoAdmin(admin.ModelAdmin):
    list_display = ('get_persona_dni', 'persona', 'estado', 'razon_social', 'categoria_laboral')

    def get_persona_dni(self, obj):
        return obj.persona.dni  # Replace 'persona' with the actual related name
    get_persona_dni.short_description = 'DNI'  # Set a custom header for the column
admin.site.register(Afiliado, AfiliadoAdmin)

class FamiliarAdmin(admin.ModelAdmin):
    list_display = ('get_persona_dni', 'persona', 'activo', )

    def get_persona_dni(self, obj):
        return obj.persona.dni  # Replace 'persona' with the actual related name
    get_persona_dni.short_description = 'DNI'  # Set a custom header for the column

admin.site.register(Familiar, FamiliarAdmin)

class RelacionFamiliarAdmin(admin.ModelAdmin):
    list_display = ('get_afiliado_persona_dni', 'tipo_relacion', 'get_familiar_persona_dni')

    def get_afiliado_persona_dni(self, obj):
        return obj.afiliado.persona.dni if obj.afiliado.persona else None

    def get_familiar_persona_dni(self, obj):
        return obj.familiar.persona.dni if obj.familiar.persona else None

    get_afiliado_persona_dni.short_description = 'Afiliado DNI'
    get_familiar_persona_dni.short_description = 'Familiar DNI'

admin.site.register(RelacionFamiliar, RelacionFamiliarAdmin)

admin.site.register(Rol)
admin.site.register(PagoCuota)
