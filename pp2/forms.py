from django import forms
from django.contrib.auth.models import User
from .models import Pedido, DireccionEnvio, DetallePedido

# Formulario de Registro de Usuario
class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Contraseña'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Confirmar Contraseña'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

    # Validación de email único
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    # Validación de contraseñas coincidentes
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

# Formulario de Pedido
class PedidoForm(forms.ModelForm):
    direccion_envio = forms.ModelChoiceField(queryset=DireccionEnvio.objects.all(), required=True, label='Dirección de Envío')

    class Meta:
        model = Pedido
        fields = ['direccion_envio']  # Incluye solo los campos del modelo Pedido

# Formulario para Detalle de Pedido (producto y cantidad)
class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad']  # Campos del modelo DetallePedido

# Formulario para Dirección de Envío
class DireccionEnvioForm(forms.ModelForm):
    class Meta:
        model = DireccionEnvio
        fields = [
            'nombres', 
            'apellidos', 
            'celular', 
            'dni', 
            'direccion', 
            'ciudad', 
            'distrito',
            'correo'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'distrito': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Distrito'}),
            'correo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo'}),
        }

# Formulario de Cliente
class ClienteForm(forms.Form):
    dni = forms.CharField(max_length=8, label='DNI')
    nombres = forms.CharField(max_length=100, label='Nombres')
    apellidos = forms.CharField(max_length=100, label='Apellidos')
    celular = forms.CharField(max_length=15, label='Celular')
    correo = forms.EmailField(label='Correo electrónico')
    departamento = forms.CharField(max_length=100, label='Departamento')
    provincia = forms.CharField(max_length=100, label='Provincia')
    distrito = forms.CharField(max_length=100, label='Distrito')
    direccion = forms.CharField(max_length=255, label='Dirección')
