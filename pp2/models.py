from django.db import models
from django.contrib.auth.models import User

# Modelo para la dirección de envío
class DireccionEnvio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=100)  # Campo para nombres
    apellidos = models.CharField(max_length=100, blank=True, null=True)  # Campo opcional
    celular = models.CharField(max_length=15)  # Campo para celular
    dni = models.CharField(max_length=8)  # Campo para DNI
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    distrito = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    correo = models.EmailField(max_length=254)  # Campo para correo

    def __str__(self):
        return f"{self.usuario.username} - {self.direccion}, {self.ciudad}, {self.distrito}, {self.pais}"

# Modelo para la Categoría de los productos
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

# Modelo para el Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    def reducir_stock(self, cantidad):
        """Método para reducir el stock al realizar un pedido"""
        self.stock -= cantidad
        self.save()

# Modelo para el Pedido
class Pedido(models.Model):
    ESTADOS = [
        ('espera', 'En espera'),
        ('aceptado', 'Pedido aceptado'),
        ('en_camino', 'En camino'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='espera')
    direccion_envio = models.ForeignKey(DireccionEnvio, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Pedido de {self.usuario.username} - {self.fecha_pedido}"

    @property
    def subtotal(self):
        """Calcula el subtotal de todos los detalles del pedido"""
        return sum(detalle.subtotal for detalle in self.detallepedido_set.all())

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en {self.pedido}"

    @property
    def subtotal(self):
        """Calcula el subtotal de este detalle"""
        return self.cantidad * self.producto.precio


# Modelo para cupones de descuento
class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)  # Porcentaje de descuento
    valido_desde = models.DateField()
    valido_hasta = models.DateField()

    def __str__(self):
        return f"Cupon {self.codigo} - {self.descuento}%"
