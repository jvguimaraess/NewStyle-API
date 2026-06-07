"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import cadastro, forgot_password, reset_password, CategoriaViewSet, ProdutoViewSet, VariacaoProdutoViewSet, UserViewSet, EnderecoViewSet, PagamentoViewSet, PedidoViewSet, ItemPedidoViewSet, CarrinhoViewSet, ItemCarrinhoViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register('categorias', CategoriaViewSet)
router.register('produtos', ProdutoViewSet, basename='produto')
router.register('variacoes', VariacaoProdutoViewSet)
router.register('users', UserViewSet)
router.register('enderecos', EnderecoViewSet, basename='endereco')
router.register('pagamentos', PagamentoViewSet, basename='pagamento')
router.register('pedidos', PedidoViewSet, basename='pedido')
router.register('itens-pedido', ItemPedidoViewSet)
router.register('carrinhos', CarrinhoViewSet)
router.register('itens-carrinho', ItemCarrinhoViewSet, basename='itemcarrinho')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/cadastro/', cadastro, name='cadastro'),
    path('api/auth/forgot-password/', forgot_password, name='forgot_password'),
    path('api/auth/reset-password/', reset_password, name='reset_password'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]