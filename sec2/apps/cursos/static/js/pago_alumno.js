// mi_script.js
var jq = $.noConflict();
var dictadosJson;
var dictadosArray
var busquedaRealizada = false

function deshabilitarResultadosPersona() {
    document.getElementById('datos_titular').innerHTML = '';

}
// Función para obtener los dictados por alumno
function obtenerDictadosPorAlumno() {
    
    document.getElementById('datos_titular').innerHTML = '';
    
    if (busquedaRealizada) {
        return
    }
    
    var enc_rol = document.getElementById('enc_alumno').value
    var url = 'get_dictados_por_alumno/';
    
    if (enc_rol && enc_rol !== '0') {
        jq.ajax({
            url: '../../' + url + enc_rol,
            type: 'GET',
            data: {},
            dataType: 'json',
            success: function(data) {
                mostrarDictados(data.dictados);
            }
        });
    }
}

// Función para mostrar los dictados en el DOM
function mostrarDictados(dictados) {
    var datosDiv = $('#datos_titular');
    var html = '<p>Seleccione el dictado:</p>';
    
    html += '<ul>';
    dictados.forEach(function(dictado) {
        
        if (dictado.tipo_pago === 1){
            var periodo = "Mes";
        }else{
            var periodo = "Clase";
        }

        html += '<label>';
        html += '<input type="checkbox" name="dictado" value="' + dictado.pk + '" data-precio="' + dictado.precio + '" data-precio_con_descuento="' + dictado.precio_con_descuento + '" data-tipo_pago="' + dictado.tipo_pago + '" data-nombre="' + dictado.nombre + '" data-aux="' + dictado.contPagosFatanes + '" data-descuento="' + dictado.descuento + '">';
        html += ' ' + dictado.nombre;
        
        if (dictado.descuento > 0) {
            html += ' $' + dictado.precio_con_descuento + ' x ' + periodo;
            html += ' (' + dictado.descuento + '% desc)';
        } else {
            html += ' $' + dictado.precio + ' x ' + periodo;
        }

        html += ' Pago ' + dictado.contPagosRealizados + ' de ' + dictado.contPagosTotalesDictado + ' (' + dictado.contPagosFatanes + ' faltantes)';
        html += '</label>';
        html += '<br>';

    });
    html += '</ul>';
    datosDiv.html(html);
}

// Función para limpiar el contenido del div
function limpiarContenido() {
    $('#datos_titular').html('');
}

function obtenerDictadosSeleccionados() {
    var dictadosSeleccionados = [];

    $('input[name="dictado"]:checked').each(function () {
        dictadosSeleccionados.push({
            valor: $(this).val(),
            nombre: $(this).data('nombre'),
            precioConDescuento: $(this).data('precio_con_descuento'),
            tipo_pago: $(this).data('tipo_pago'),
            descuento: $(this).data('descuento'),
            precio: $(this).data('precio'), // Obtiene el precio desde el atributo data-precio
            cantidad: 1,
            aux: $(this).data('aux'),
        });
    });

    return dictadosSeleccionados;
}

function calcularTotalSubtotales(dictadosSeleccionados) {
    var totalSubtotales = 0;

    for (var i = 0; i < dictadosSeleccionados.length; i++) {
        totalSubtotales += parseFloat(dictadosSeleccionados[i].precioConDescuento);
    }
    // Redondear el resultado a dos decimales
    totalSubtotales = totalSubtotales.toFixed(2);
    return totalSubtotales;
}

function generarTablaHTML(dictadosSeleccionados, totalSubtotales) {
    var tableHTML = '<table class="table table-sm table-hover">';
    tableHTML += '<thead>';
    tableHTML += '<tr>';
    tableHTML += '<th>Descripción</th>';
    tableHTML += '<th class="text-end">Precio</th>';
    tableHTML += '<th class="text-center">Desc</th>';
    tableHTML += '<th class="text-end">Precio (desc)</th>';
    tableHTML += '<th> Periodo </th>';
    tableHTML += '<th class="text-center">Cantidad</th>';
    tableHTML += '<th class="text-end">SubTotal</th>';
    tableHTML += '</tr>';
    tableHTML += '</thead>';
    tableHTML += '<tbody>';

    for (var i = 0; i < dictadosSeleccionados.length; i++) {
        tableHTML += '<tr>';
        tableHTML += '<td>' + dictadosSeleccionados[i].nombre + '</td>';
        tableHTML += '<td class="text-end">$' + dictadosSeleccionados[i].precio + '</td>';
        tableHTML += '<td class="text-center">' + dictadosSeleccionados[i].descuento + '%</td>';
        tableHTML += '<td class="text-end">$' + dictadosSeleccionados[i].precioConDescuento + '</td>';

        if (dictadosSeleccionados[i].tipo_pago === 1 ){
            tableHTML += '<td class="text-center"> x Mes </td>';
        }else{
            tableHTML += '<td class="text-center"> x Clase </td>';
        }

        tableHTML += '<td class="text-center"><input type="number" class="cantidad form-control smaller-input" value="' + dictadosSeleccionados[i].cantidad + '" min="1" data-index="' + i + '"></td>';

        var precioTotal = dictadosSeleccionados[i].precioConDescuento * dictadosSeleccionados[i].cantidad;
        tableHTML += '<td class="subtotal text-end">$' + precioTotal.toFixed(2) + '</td>';
        tableHTML += '</tr>';
    }

    tableHTML += '</tbody>';
    tableHTML += '</table>';
    tableHTML += '<p class="text-end" id="totalSubtotales">TOTAL: <strong>$' + totalSubtotales + '</strong></p>';
    $('#total_a_pagar').val(totalSubtotales);
    return tableHTML;
}

// Función para actualizar el valor del input dictados_seleccionados
function actualizarInputDictados(dictadosSeleccionados) {
    dictadosArray = dictadosSeleccionados
    dictadosJson = JSON.stringify(dictadosSeleccionados);
    $('#dictados_seleccionados').val(dictadosJson);
}

// Captura el cambio en los checkboxes y actualiza la sección 2
$(document).on('change', 'input[name="dictado"]', function () {
    var dictadosSeleccionados = obtenerDictadosSeleccionados();
    actualizarInputDictados(dictadosSeleccionados);

    var totalSubtotales = calcularTotalSubtotales(dictadosSeleccionados);
    var tableHTML = generarTablaHTML(dictadosSeleccionados, totalSubtotales);
    $('#seleccionados').html(tableHTML);
});

function cantidadAceptada(cantidad) {
    return cantidad >= 1 && !isNaN(cantidad);
}

function indiceValido(index) {
    return index >= 0;
}

// Captura el cambio en los campos de cantidad y actualiza los subtotales
$(document).on('change', '.cantidad', function () {
    var index = $(this).data('index'); // Obtiene el índice del elemento seleccionado
    var cantidad = parseInt($(this).val());

    // Verifica si la cantidad es aceptada
    if (!cantidadAceptada(cantidad)) {
        $(this).val(1); // Establece la cantidad a 1 si no es aceptada
        cantidad = 1;
    }

    // Calcula el subtotal
    var precioTotal = parseFloat($(this).closest('tr').find('td:nth-child(4)').text().replace('$', '')); // Obtiene el precio con descuento
    var subtotal = cantidad * precioTotal;
    $(this).closest('tr').find('.subtotal').text('$' + subtotal.toFixed(2)); // Actualiza el subtotal en la tabla

    // Actualiza la cantidad en los dictados seleccionados
    dictadosArray[index].cantidad = cantidad;

    // Actualiza el valor del input dictados_seleccionados
    actualizarInputDictados(dictadosArray);

    // Recalcula el total de subtotales
    var totalSubtotales = 0;
    $('.subtotal').each(function () {
        totalSubtotales += parseFloat($(this).text().replace('$', ''));
    });
    $('#totalSubtotales').html('TOTAL : $<strong>' + totalSubtotales.toFixed(2) + '</strong>');
    $('#total_a_pagar').val(totalSubtotales.toFixed(2));
});


// Ejecutar funciones al cargar el documento
// jq(document).ready(function() {
    // obtenerDictadosPorAlumno();
// });
