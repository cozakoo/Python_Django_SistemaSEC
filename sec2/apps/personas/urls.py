from django.urls import path
from .views import *
# from apps.personas.views import

app_name="personas"

urlpatterns = [
    # ----------------- PERSONAS -----------------
    path('mostrar-detalle-persona/', mostrarPersona , name='mostrar_detalle_persona'),
]

