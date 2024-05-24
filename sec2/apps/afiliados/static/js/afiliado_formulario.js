$(document).ready(function () {
    var currentTab = 1

    function updateButtons() {
        if (currentTab === 1) {
            $('#prev-button').hide()
        } else {
            $('#prev-button').show()
        }
        
        if (currentTab === 2) {
            $('#next-button').hide()
            $("button[type='submit']").show()
            
        } else {
            $('#next-button').show()
            $("button[type='submit']").hide()
        }
        $('#submit-button').show()
    }

    updateButtons() // Llama a esta función al cargar la página

    $('#next-button').click(function (e) {
        e.preventDefault() // Previene el comportamiento predeterminado del botón

        if (currentTab === 1) {
            $('#section1').removeClass('show active')
            $('#tab-section-1').removeClass('active')
            $('#section2').addClass('show active')
            $('#tab-section-2').addClass('active')
            currentTab = 2
        } else if (currentTab === 2) {
            // Aquí puedes realizar validaciones antes de avanzar
        }
        updateButtons() // Actualiza los botones
    })

    $('#prev-button').click(function (e) {
        e.preventDefault() // Previene el comportamiento predeterminado del botón

        if (currentTab === 2) {
            $('#section2').removeClass('show active')
            $('#tab-section-2').removeClass('active')
            $('#section1').addClass('show active')
            $('#tab-section-1').addClass('active')
            currentTab = 1
        }
        updateButtons() // Actualiza los botones
    })
})