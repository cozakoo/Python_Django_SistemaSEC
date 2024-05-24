document.addEventListener('DOMContentLoaded', function () {
    const submenuButtons = document.querySelectorAll('.submenu-toggle')

    submenuButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const submenu = button.nextElementSibling
            submenu.classList.toggle('show');
        })
    })
});