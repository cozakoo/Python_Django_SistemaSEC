    // Variable para evitar múltiples búsquedas simultáneas
    // var busquedaRealizada = false

    // Función para realizar la búsqueda de persona por DNI
    function buscarPersona() {
      // Verificar si ya se realizó una búsqueda
    //   if (busquedaRealizada) {
        // console.log('Búsqueda ya realizada, evitando otra solicitud.')
        // return
    //   }

      // Obtener el valor del DNI
      var dni = document.getElementById('dni').value

      // Validar el formato del DNI
      if (!dni) {
        alert('Por favor, ingrese un número de DNI.')
        return
      }

      if (dni.length !== 8) {
        alert('El DNI debe tener exactamente 8 dígitos.')
        return
      }

      // Marcar la búsqueda como realizada
      busquedaRealizada = true

      // Realizar la llamada AJAX
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "{% url 'cursos:buscar_persona' %}?dni=" + dni, true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          // Procesar la respuesta
          var respuesta = JSON.parse(xhr.responseText);
          mostrarResultados(respuesta.persona);
        }
      };
      xhr.send();
    }

    // Función para mostrar los resultados en la página
    function mostrarResultados(persona) {
      var resultadosDiv = document.getElementById('resultadosPersona');

      if (persona) {
        // Persona encontrada, mostrar detalles
        resultadosDiv.innerHTML = `
          <p>DNI: ${persona.dni}</p>
          <p>Nombre: ${persona.nombre} ${persona.apellido}</p>
          <!-- Agregar más detalles según sea necesario -->
        `;
      } else {
        // Persona no encontrada
        resultadosDiv.innerHTML = '<p>Persona no encontrada para el DNI ingresado.</p>';
      }
    }