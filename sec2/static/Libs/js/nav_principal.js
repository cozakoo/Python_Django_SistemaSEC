var jq = $.noConflict();


jq(document).ready(function () {
    $('#mostrarMenuAfiliado').click(function () {
        $('#menu_principal').hide();
        $('#menu_afiliado_principal').show();
        $('#menu_curso_principal').hide();
        $('#menu_usuarios_principal').hide();
    });

    $('#mostrarMenuCurso').click(function () {
        $('#menu_principal').hide();
        $('#menu_afiliado_principal').hide();
        $('#menu_curso_principal').show();
        $('#menu_usuarios_principal').hide();

    });

    $('#mostrarMenuSalon').click(function () {
        $('#menu_principal').hide();
        $('#menu_afiliado_principal').hide();
        $('#menu_curso_principal').hide();
        $('#menu_usuarios_principal').hide();
        $('#menu_salon_principal').show();
    });

    $('#mostrarMenuUsers').click(function () {
        $('#menu_principal').hide();
        $('#menu_afiliado_principal').hide();
        $('#menu_curso_principal').hide();
        $('#menu_salon_principal').hide();
        $('#menu_usuarios_principal').show();
    });

    // Agrega una función para mostrar/ocultar el menú de afiliados
    $('#mostrarMenuGestionAfiliados').click(function () {
        $('#menu_afiliado_principal').show();
        $('#menu_curso_principal').hide();
        $('#menu_usuarios_principal').hide();
    });

    // Agrega una función para mostrar/ocultar el menú de cursos
    $('#mostrarMenuGestionCursos').click(function () {
        $('#menu_afiliado_principal').hide();
        $('#menu_curso_principal').show();
        $('#menu_usuarios_principal').hide();

    });

    // Agrega una función para ocultar el menú de afiliados
    $('#ocultarMenuAfiliados').click(function () {
        $('#menu_afiliado_principal').hide();
    });

    // Agrega una función para ocultar el menú de cursos
    $('#ocultarMenuCursos').click(function () {
        $('#menu_curso_principal').hide();
    });
});
