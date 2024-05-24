var jq = $.noConflict();

function loadDictadosPorAlumno() {
    jq('#enc_alumno').change(function() {
        var rol_id = jq(this).val();
        var url = 'get_dictados_por_alumno/';

        if (rol_id && rol_id !== '0') {
            jq.ajax({
                url: '../../' + url + rol_id,
                type: 'GET',
                data: {},
                dataType: 'json',
                success: function(data) {
                    var datosDiv = $('#datos_titular');
                    var html = '<p>Seleccione el dictado:</p>';

                    html += '<ul>';
                    data.dictados.forEach(function(dictado) {
                        html += '<label>';
                        html += '<input type="checkbox" name="dictado" value="' + dictado.pk + '" data-precio="' + dictado.precio + '" data-precio_con_descuento="' + dictado.precio_con_descuento + '" data-tipo_pago="' + dictado.tipo_pago + '" data-nombre="' + dictado.nombre + '" data-contPagosFatanes="' + dictado.contPagosFatanes + " data-descuento="' + dictado.descuento + '">';
                        html += ' ' + dictado.nombre;
                        if (dictado.descuento > 0) {
                            html += ' $' + dictado.precio_con_descuento + ' ' + dictado.tipo_pago;
                            html += ' (Descuento aplicado)';
                        } else {
                            html += ' $' + dictado.precio + ' ' + dictado.tipo_pago;
                        }
                        html += '</label>';
                    });
                    html += '</ul>';
                    datosDiv.html(html);
                }
            });
        } else {
            $('#datos_titular').html('');
        }
    });
}
