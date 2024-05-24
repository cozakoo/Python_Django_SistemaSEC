$(document).ready(function() {
    $('#enc_profesor').change(function() {
        console.log("INICIO")
        var titular_id = $(this).val();
        url = '../get_dictados_por_titular/' + titular_id + '/';
        
        console.log(url)

        if (titular_id) {
            event.preventDefault();
            $.ajax({
                type:'GET',
                url: {% url 'cursos:get_dictados_por_titular" %},
                data: {
                    "titular_id": titular_id,
                },
                dataType: 'json',
                success: function(data) {
                    $('#enc_dictado').empty();
                    $.each(data, function(index, dictado) {
                        $('#enc_dictado').append('<option value="' + dictado.id + '">' + dictado.nombre + '</option>');
                    });
                }
            });
        }
    });
});