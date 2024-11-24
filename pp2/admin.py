from django import forms 
from django.contrib import admin
from .models import Categoria, Producto, Pedido, DireccionEnvio, Cupon, DetallePedido

# Configuración personalizada para la administración de productos
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'disponible', 'categoria')
    list_filter = ('disponible', 'categoria')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'disponible')

# Configuración personalizada para la administración de pedidos
class PedidoForm(forms.ModelForm):
    # Campos que deseas mostrar
    nombres = forms.CharField(max_length=100, required=False)
    apellidos = forms.CharField(max_length=100, required=False)
    dni = forms.CharField(max_length=8, required=False)
    celular = forms.CharField(max_length=15, required=False)
    correo = forms.EmailField(required=False)
    direccion = forms.CharField(max_length=255, required=False)
    distrito = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Pedido
        fields = '__all__'  # Incluye todos los campos del modelo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            # Obtener la dirección de envío relacionada
            if self.instance.direccion_envio:
                direccion = self.instance.direccion_envio
                # Asignar los valores a los campos del formulario
                self.fields['nombres'].initial = direccion.nombres
                self.fields['apellidos'].initial = direccion.apellidos
                self.fields['dni'].initial = direccion.dni
                self.fields['celular'].initial = direccion.celular
                self.fields['correo'].initial = direccion.correo
                self.fields['direccion'].initial = direccion.direccion
                self.fields['distrito'].initial = direccion.distrito

# Configuración personalizada para la administración de pedidos
class PedidoAdmin(admin.ModelAdmin):
    form = PedidoForm  # Usar el formulario personalizado
    list_display = ('usuario', 'mostrar_productos', 'mostrar_cantidades', 'fecha_pedido', 'estado')
    list_filter = ('fecha_pedido', 'usuario', 'estado')
    search_fields = ('usuario__username',)

    # Métodos para mostrar productos y cantidades
    def mostrar_productos(self, obj):
        return ", ".join([detalle.producto.nombre for detalle in obj.detallepedido_set.all()])
    mostrar_productos.short_description = 'Productos'

    def mostrar_cantidades(self, obj):
        return ", ".join([str(detalle.cantidad) for detalle in obj.detallepedido_set.all()])
    mostrar_cantidades.short_description = 'Cantidades'



# Configuración personalizada para la administración de categorías
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

# Configuración personalizada para la administración de direcciones
class DireccionEnvioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'direccion', 'ciudad', 'distrito', 'pais', 'correo')
    search_fields = ('usuario__username', 'direccion')

# Configuración personalizada para la administración de cupones
class CuponAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descuento', 'valido_desde', 'valido_hasta')
    search_fields = ('codigo',)

# Registrar los modelos con la configuración personalizada
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(DireccionEnvio, DireccionEnvioAdmin)
admin.site.register(Cupon, CuponAdmin)
