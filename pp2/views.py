from itertools import product
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Producto, Categoria, Pedido, DetallePedido
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistroUsuarioForm, PedidoForm
from django.core.paginator import Paginator
from .forms import DireccionEnvioForm
from .forms import RegistroUsuarioForm, PedidoForm, DireccionEnvioForm, ClienteForm, DetallePedidoForm  # Agrega ClienteForm aquí


# Vista para la página de inicio
def inicio(request):
    productos_destacados = Producto.objects.filter(disponible=True)[:4]  # Ejemplo de productos destacados
    productos_aleatorios = Producto.objects.filter(disponible=True).order_by('?')[:3]  # Seleccionar 3 productos aleatorios
    return render(request, 'inicio.html', {'productos_destacados': productos_destacados, 'productos_aleatorios': productos_aleatorios})


# Vista para la página de productos
def productos(request):
    # Obtener todos los productos disponibles
    productos = Producto.objects.filter(disponible=True)

    # Filtrar por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        # Filtrar productos por la categoría seleccionada
        productos = productos.filter(categoria__nombre=categoria)
        # Guardar la categoría seleccionada para usarla después en el filtro de precio
        categoria_seleccionada = categoria
    else:
        categoria_seleccionada = None

    # Filtrar por precio si hay una categoría seleccionada
    precio = request.GET.get('precio')
    if precio and categoria_seleccionada:  # Solo aplicar el filtro de precio si hay una categoría
        productos = productos.filter(precio__lte=precio)

    # Paginación: 12 productos por página
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'productos.html', {'page_obj': page_obj, 'categoria_seleccionada': categoria_seleccionada})


# Vista para ver los detalles de un producto
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'detalle_producto.html', {'producto': producto})

# Vista para registrar usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('inicio')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro.html', {'form': form})

# Vista para iniciar sesión
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Redirigir al carrito si es que estaba intentando realizar una compra
                next_url = request.GET.get('next', 'inicio')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def salir(request):
    logout(request)
    messages.success(request, "Tu sesión se ha cerrado correctamente")
    return redirect('inicio')

# Vista para crear un pedido
@login_required
def crear_pedido(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        # Aquí solo manejas la cantidad y la adición al carrito
        cantidad = int(request.POST.get('cantidad', 1))

        # Obtener el carrito de la sesión
        carrito = request.session.get('carrito', [])
        
        # Verificar si el producto ya está en el carrito
        producto_encontrado = False
        for item in carrito:
            if item['producto_id'] == producto.id:
                item['cantidad'] += cantidad
                producto_encontrado = True
                break

        # Si no está, añadir un nuevo item
        if not producto_encontrado:
            carrito.append({
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': cantidad
            })

        # Actualizar el carrito en la sesión
        request.session['carrito'] = carrito
        request.session.modified = True  # Asegura que Django guarda los cambios en la sesión

        # Redirigir al carrito después de agregar el producto
        return redirect('ver_carrito')  # Cambia aquí
    else:
        # Solo se necesita el formulario para el pedido si es necesario
        return render(request, 'crear_pedido.html', {'producto': producto})



# Vista para ver el carrito de compras
@login_required
def ver_carrito(request):
    # Recuperar el carrito desde la sesión
    carrito = request.session.get('carrito', [])
    
    print(f"Carrito al ver: {carrito}")  # Verifica lo que está almacenado en la sesión
    
    # Calcular el total general de la compra
    total_general = sum(item['precio'] * item['cantidad'] for item in carrito)

    # Obtener productos desde la base de datos para asegurarnos de que podemos acceder a todos sus datos
    productos_ids = [item['producto_id'] for item in carrito]
    productos = Producto.objects.filter(id__in=productos_ids)

    # Crear una lista de pedidos que contenga los objetos Producto
    pedidos = []
    for item in carrito:
        producto = productos.get(id=item['producto_id'])
        pedidos.append({
            'producto': producto,
            'cantidad': item['cantidad'],
            'subtotal': producto.precio * item['cantidad'],
            'id': producto.id  # Agregar el ID del producto
        })

    return render(request, 'carrito.html', {'pedidos': pedidos, 'total': total_general})

# Vista para finalizar compra
# Vista para finalizar compra
@login_required
def finalizar_compra(request):
    # Obtén el carrito de la sesión
    carrito = request.session.get('carrito', [])

    # Solo proceder si el carrito no está vacío
    if not carrito:
        messages.warning(request, "Agregue un producto para realizar la compra.")
        return redirect('ver_carrito')  # Redirigir a la vista del carrito

    # Inicializa el formulario de dirección
    if request.method == 'POST':
        direccion_form = DireccionEnvioForm(request.POST)

        # Verifica si el formulario es válido
        if direccion_form.is_valid():
            # Guarda la dirección de envío
            direccion_envio = direccion_form.save(commit=False)
            direccion_envio.usuario = request.user  # Asociar la dirección al usuario
            direccion_envio.save()

            # Crea el pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                direccion_envio=direccion_envio,
                estado='espera'
            )

            # Crea un detalle por cada producto en el carrito
            for item in carrito:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto_id=item['producto_id'],  # Asegúrate de que este ID esté en el carrito
                    cantidad=item['cantidad']
                )

            # Limpiar el carrito después de finalizar la compra
            request.session['carrito'] = []

            return redirect('mi_cuenta')  # Redirige a una vista de éxito

    else:
        # Si es una solicitud GET, solo inicializa el formulario
        direccion_form = DireccionEnvioForm()

    return render(request, 'finalizar_compra.html', {
        'direccion_form': direccion_form,
        'carrito': carrito,  # Puedes pasar el carrito si necesitas mostrarlo en la plantilla
    })



# Vista para ver la cuenta del usuario
@login_required
def mi_cuenta(request):
    return render(request, 'mi_cuenta.html')

# Vista para ver los pedidos del usuario
@login_required
def pedidos_view(request):
    # Filtra los pedidos que se han completado (puedes ajustar la condición según necesites)
    pedidos = Pedido.objects.filter(usuario=request.user, ).order_by('-fecha_pedido')

    if not pedidos:
        return render(request, 'pedidos.html', {'pedidos': pedidos})

    return render(request, 'pedidos.html', {'pedidos': pedidos})

# Vista para actualizar un pedido (opcional, según sea necesario)
@login_required
def actualizar_pedido(request, producto_id):
    # Recuperar el pedido desde la sesión
    carrito = request.session.get('carrito', [])
    pedido = next((item for item in carrito if item['producto_id'] == producto_id), None)

    if request.method == 'POST' and pedido is not None:
        action = request.POST.get('action')
        producto = Producto.objects.get(id=producto_id)
        
        if action == 'increase':
            pedido['cantidad'] += 1
        elif action == 'decrease' and pedido['cantidad'] > 1:
            pedido['cantidad'] -= 1
            
        # Actualiza el subtotal después de cambiar la cantidad
        pedido['subtotal'] = float(producto.precio) * pedido['cantidad']

    # Guardar los cambios en el carrito
    request.session['carrito'] = carrito
        
    return redirect('ver_carrito')

# Vista para eliminar un pedido
@login_required
def eliminar_pedido(request, producto_id):
    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', [])

    # Filtrar los productos que no correspondan al producto que queremos eliminar
    nuevo_carrito = [item for item in carrito if item['producto_id'] != producto_id]

    # Actualizar el carrito en la sesión
    request.session['carrito'] = nuevo_carrito
    request.session.modified = True  # Asegura que los cambios se guardan en la sesión

    # Redirigir al carrito después de eliminar el producto
    return redirect('ver_carrito')

# Vista para agregar al carrito
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', [])
    
    # Verificar si el producto ya está en el carrito
    producto_encontrado = False
    for item in carrito:
        if item['producto_id'] == producto_id:
            item['cantidad'] += cantidad
            producto_encontrado = True
            break

    # Si no está, añadir un nuevo item
    if not producto_encontrado:
        carrito.append({
            'producto_id': producto.id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'cantidad': cantidad
        })

    # Actualizar el carrito en la sesión
    request.session['carrito'] = carrito
    request.session.modified = True  # Asegura que Django guarda los cambios en la sesión

    return redirect('ver_carrito')

# Vista para ver detalles del pedido
# Vista para ver detalles del pedido
@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    # Solo pasa el pedido sin la dirección de envío
    return render(request, 'detalle_pedido.html', {'pedido': pedido})


# Vista para la confirmación del pedido
@login_required
def confirmacion_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'detalle_pedido.html', {'pedido': pedido})

def buscar_productos_ajax(request):
    query = request.GET.get('q', '')
    productos = Producto.objects.filter(nombre__icontains=query)[:5] #Limitar los resultados a 5
    resultados = []
    for producto in productos:
        resultados.append({
            'id': producto.id,
            'nombre':producto.nombre,
            'imagen': producto.imagen.url,
            'url': f'/productos7{producto.id}/' 
        })
    return JsonResponse(resultados, safe=False)