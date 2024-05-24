// Seleccionar todos los elementos con la clase .alert-dismissible dentro de #messages-container
var alertElements = document.querySelectorAll('#messages-container .alert-dismissible');

// Iterar a través de los elementos y agregar un temporizador de 5 segundos para desvanecerlos
alertElements.forEach(function (alertElement) {
    setTimeout(function () {
        alertElement.classList.add('fade');
    }, 5000); // 5000 milisegundos (5 segundos)
});