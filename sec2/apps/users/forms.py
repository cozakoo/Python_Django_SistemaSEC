from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth.models import User
 


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)



class UserRegisterForm(UserCreationForm):
    
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    permiso_gestion_afiliados = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    permiso_gestion_cursos = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    permiso_gestion_salon = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    permiso_gestion_usuarios = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User  
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre existente, ingrese uno distinto")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        print("asdasd")
        # Validar que el correo electrónico sea único
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso. Por favor, elige otro.")
        
        # Validar que el correo electrónico incluya un signo @
        if '@' not in email:
            raise forms.ValidationError("El correo electrónico debe incluir un signo @.")
        
        return email
    


    


    
    
    