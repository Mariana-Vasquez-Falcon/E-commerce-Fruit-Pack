"""pp1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from pp2 import views  # Importa las vistas desde pp2
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from pp2 import views




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('productos/', views.productos, name='productos'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('crear_pedido/<int:producto_id>/', views.crear_pedido, name='crear_pedido'),
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('pedidos/', views.pedidos_view, name='pedidos'),
    path('carrito/actualizar/<int:pedido_id>/', views.actualizar_pedido, name='actualizar_pedido'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('confirmacion-pedido/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    

]

# Solo para desarrollo: para servir archivos de medios (imágenes, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

