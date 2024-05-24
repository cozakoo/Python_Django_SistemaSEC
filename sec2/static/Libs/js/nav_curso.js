const submenuButtons = document.querySelectorAll('.submenu-toggle')

submenuButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const submenu = button.nextElementSibling
        if (submenu.style.display === 'block') {
            submenu.style.display = 'none'
        } else {
            submenu.style.display = 'block'
        }
    })
})
