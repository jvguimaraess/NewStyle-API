from rest_framework import viewsets
from .models import Categoria, Produto, VariacaoProduto, User, Pedido, ItemPedido, Carrinho, ItemCarrinho
from .serializers import CategoriaSerializer, ProdutoSerializer, VariacaoProdutoSerializer, UserSerializer, PedidoSerializer, ItemPedidoSerializer, CarrinhoSerializer, ItemCarrinhoSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsLojista, IsCliente
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

@api_view(['POST'])
@permission_classes([AllowAny])
def cadastro(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria']
    search_fields = ['nome', 'descricao']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'lojista':
            if self.action in ['list', 'retrieve']:
                return Produto.objects.filter(ativo=True)
            return Produto.objects.filter(lojista=user, ativo=True)
        return Produto.objects.filter(ativo=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsLojista()]

    def perform_create(self, serializer):
        serializer.save(lojista=self.request.user)

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