from audioop import reverse
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
# from ..models import Actividad, Curso, Dictado, Aula, Alumno, Asistencia_alumno, Asistencia_profesor, Titular
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import permission_required , login_required 

@permission_required('cursos.permission_gestion_curso', raise_exception=True)
@login_required(login_url='/login/')
def index(request):
    template = loader.get_template('home_curso.html')
    return HttpResponse(template.render())

# def registrarAsistenciaAlumno(request, pk, apk):
#     asistencia_alumno = Asistencia_alumno(dictado_id=pk, alumno_id=apk)
#     asistencia_alumno.save()
#     dictado = Dictado.objects.get(pk=pk)
#     curso = Curso.objects.get(pk=dictado.curso.pk)
#     return redirect('cursos:alumnos_dictado',curso.pk)   

# def registrarAsistenciaProfesor(request, pk, ppk):
#     titular = Titular.objects.filter(titular_dictado_pk=pk)
#     asistencia_profesor = Asistencia_profesor(titular)
#     asistencia_profesor.save()

# def registrarAlumnoADictado(request, pk, apk):
#     alumno = Alumno.objects.get(pk=apk)
#     dictado = alumno.agregateDictado(pk)
#     return redirect('cursos:alumnos_dictado', dictado.pk)



 

