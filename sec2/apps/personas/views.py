from django.shortcuts import get_object_or_404, render

from apps.afiliados.models import Afiliado, Familiar, RelacionFamiliar
from .forms import *
from .models import *
from django.shortcuts import redirect

def mostrarPersona(request):
    if request.method == 'GET':
        print("ESTOY EN UN GET")
        dni = request.GET.get('dni')
        print("dni", dni)
    else:
        print("ESTOY EN UN SET")

    return redirect('home')

    
    # persona_id = request.GET.get('enc_cliente')
    # if persona_id is not None or persona_id != 0:
    #     # Obtener la persona seleccionada
    #     persona = get_object_or_404(Persona, pk=persona_id)
        
    #     # Obtener el rol asociado a la persona
    #     rol = get_object_or_404(Rol, persona=persona)

    #     if rol.tipo == ROL_TIPO_AFILIADO:
    #         afiliado = get_object_or_404(Afiliado, persona=persona)
    #         return redirect('afiliados:afiliado_detalle', pk=afiliado.pk)
    #     elif rol.tipo == ROL_TIPO_FAMILIAR:
    #         familiar = get_object_or_404(Familiar, persona=persona)
    #         relacion = get_object_or_404(RelacionFamiliar, familiar=familiar)
    #         return redirect('afiliados:familiar_detalle', pk=relacion.afiliado.pk, familiar_pk=familiar.pk, ventana='misma_ventana')
    #     return render(request, 'mostrar_persona.html', {'rol': rol})
    
