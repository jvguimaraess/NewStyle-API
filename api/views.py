from rest_framework import viewsets
from .models import Categoria, Produto, VariacaoProduto, User, Pedido, ItemPedido, Carrinho, ItemCarrinho
from .serializers import CategoriaSerializer, ProdutoSerializer, VariacaoProdutoSerializer, UserSerializer, PedidoSerializer, ItemPedidoSerializer, CarrinhoSerializer, ItemCarrinhoSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

class VariacaoProdutoViewSet(viewsets.ModelViewSet):
    queryset = VariacaoProduto.objects.all()
    serializer_class = VariacaoProdutoSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

class CarrinhoViewSet(viewsets.ModelViewSet):
    queryset = Carrinho.objects.all()
    serializer_class = CarrinhoSerializer

class ItemCarrinhoViewSet(viewsets.ModelViewSet):
    queryset = ItemCarrinho.objects.all()
    serializer_class = ItemCarrinhoSerializer