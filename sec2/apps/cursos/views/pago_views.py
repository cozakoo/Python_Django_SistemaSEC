# from ..models import Pago_alumno
# from ..forms.pago_alumno_forms import *
# from django.views.generic.edit import CreateView
# from django.urls import reverse_lazy

# class PagoAlumnoCreateView(CreateView):
#     model = Pago_alumno
#     form_class = FormularioPagoAlumno
#     template_name = 'otro/pago_alumno_form.html'  
#     success_url = reverse_lazy('cursos:cursos')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['titulo'] = "Listado de profesores"
#         return context