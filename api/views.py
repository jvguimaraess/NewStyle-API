from rest_framework import viewsets
from .models import Categoria, Produto, VariacaoProduto, User, Endereco, Pagamento, Pedido, ItemPedido, Carrinho, ItemCarrinho
from .serializers import CategoriaSerializer, ProdutoSerializer, VariacaoProdutoSerializer, UserSerializer, EnderecoSerializer, PagamentoSerializer, PedidoSerializer, ItemPedidoSerializer, CarrinhoSerializer, ItemCarrinhoSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action, api_view, permission_classes
from .permissions import IsLojista, IsCliente
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction

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

class EnderecoViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [IsCliente]

    def get_queryset(self):
        return Endereco.objects.filter(cliente=self.request.user)

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

class PagamentoViewSet(viewsets.ModelViewSet):
    serializer_class = PagamentoSerializer
    permission_classes = [IsCliente]

    def get_queryset(self):
        return Pagamento.objects.filter(cliente=self.request.user)

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer

    def get_permissions(self):
        if self.action == 'finalizar':
            return [IsCliente()]
        if self.action == 'atualizar_status':
            return [IsLojista()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'lojista':
            return Pedido.objects.filter(
                itens__variacao__produto__lojista=user).distinct().order_by('created_at')
        return Pedido.objects.filter(cliente=user)

    @action(detail=False, methods=['post'])
    def finalizar(self, request):
        carrinho = Carrinho.objects.get(cliente=request.user)
        itens = carrinho.itens.all()

        if not itens.exists():
            return Response(
                {'detail': 'O carrinho está vazio.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        endereco_id = request.data.get('endereco')
        pagamento_id = request.data.get('pagamento')

        with transaction.atomic():
            pedido = Pedido.objects.create(
                cliente=request.user,
                endereco_id=endereco_id,
                pagamento_id=pagamento_id,
                status='pendente'
            )

            total = 0
            for item in itens:
                if item.quantidade > item.variacao.estoque:
                    raise serializers.ValidationError(
                        f'Estoque insuficiente para {item.variacao}.'
                    )

                ItemPedido.objects.create(
                    pedido=pedido,
                    variacao=item.variacao,
                    quantidade=item.quantidade,
                    preco_unitario=item.variacao.preco
                )

                item.variacao.estoque -= item.quantidade
                item.variacao.save()

                total += item.variacao.preco * item.quantidade

            pedido.total = total
            pedido.save()

            itens.delete()

        serializer = self.get_serializer(pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def atualizar_status(self, request, pk=None):
        pedido = self.get_object()
        novo_status = request.data.get('status')

        STATUS_VALIDOS = ['pendente', 'confirmado', 'cancelado']
        if novo_status not in STATUS_VALIDOS:
            return Response(
                {'detail': 'Status inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedido.status = novo_status
        pedido.save()

        serializer = self.get_serializer(pedido)
        return Response(serializer.data)
class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

class CarrinhoViewSet(viewsets.ModelViewSet):
    queryset = Carrinho.objects.all()
    serializer_class = CarrinhoSerializer

class ItemCarrinhoViewSet(viewsets.ModelViewSet):
    serializer_class = ItemCarrinhoSerializer
    permission_classes = [IsCliente]

    def get_queryset(self):
        carrinho = Carrinho.objects.get(cliente=self.request.user)
        return ItemCarrinho.objects.filter(carrinho=carrinho)

    def perform_create(self, serializer):
        carrinho = Carrinho.objects.get(cliente=self.request.user)
        serializer.save(carrinho=carrinho)