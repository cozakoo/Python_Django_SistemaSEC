from django import template

register = template.Library()

@register.filter(name='user_has_perm')
def user_has_perm(user, permission):
    return user.has_perm(permission)
