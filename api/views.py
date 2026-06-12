from .models import Categoria, Produto, VariacaoProduto, User, Endereco, Pagamento, Pedido, ItemPedido, Carrinho, ItemCarrinho
from .serializers import CategoriaSerializer, ProdutoSerializer, VariacaoProdutoSerializer, UserSerializer, EnderecoSerializer, PagamentoSerializer, PedidoSerializer, ItemPedidoSerializer, CarrinhoSerializer, ItemCarrinhoSerializer
from .permissions import IsLojista, IsCliente
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings

@api_view(['POST'])
@permission_classes([AllowAny])
def cadastro(request):
    """Cadastra um novo usuário (lojista ou cliente). Endpoint público."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Solicita recuperação de senha. Gera um token seguro e envia
    um link de redefinição para o email informado. Por segurança,
    não revela se o email está ou não cadastrado.
    """
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Se o email existir, um link será enviado.'},
            status=status.HTTP_200_OK
        )

    token = PasswordResetTokenGenerator().make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    link = f'{settings.FRONTEND_URL}/api/auth/reset-password/?uid={uid}&token={token}'

    send_mail(
        'Recuperação de senha',
        f'Use o link para redefinir sua senha: {link}',
        None,
        [email],
    )

    return Response(
        {'detail': 'Se o email existir, um link será enviado.'},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Redefine a senha do usuário a partir de um token válido.
    Valida o token, a força da nova senha, e a salva criptografada.
    """
    uid = request.data.get('uid')
    token = request.data.get('token')
    nova_senha = request.data.get('nova_senha')

    if not uid or not token or not nova_senha:
        return Response(
            {'detail': 'Dados incompletos.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response(
            {'detail': 'Link inválido.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not PasswordResetTokenGenerator().check_token(user, token):
        return Response(
            {'detail': 'Token inválido ou expirado.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(nova_senha) < 8:
        return Response(
            {'detail': 'A senha deve ter no mínimo 8 caracteres.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(nova_senha)
    user.save()

    return Response(
        {'detail': 'Senha redefinida com sucesso.'},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def contato(request):
    """
    Recebe uma mensagem de contato e a envia por email para a
    plataforma. Valida campos obrigatórios e tamanho da mensagem.
    """
    nome = request.data.get('nome')
    email = request.data.get('email')
    assunto = request.data.get('assunto')
    mensagem = request.data.get('mensagem')

    if not all([nome, email, assunto, mensagem]):
        return Response(
            {'detail': 'Todos os campos são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_email(email)
    except DjangoValidationError:
        return Response(
            {'detail': 'Email inválido.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(mensagem) < 10 or len(mensagem) > 1000:
        return Response(
            {'detail': 'A mensagem deve ter entre 10 e 1000 caracteres.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        send_mail(
            f'[Contato] {assunto}',
            f'Nome: {nome}\nEmail: {email}\n\nMensagem:\n{mensagem}',
            None,
            ['joaoalbarello@ejectufrn.com.br'],
        )
    except Exception:
        return Response(
            {'detail': 'Erro ao enviar a mensagem. Tente novamente.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {'detail': 'Mensagem enviada com sucesso.'},
        status=status.HTTP_200_OK
    )
    
class CategoriaViewSet(viewsets.ModelViewSet):
    """
    Gerencia categorias de produtos. Qualquer usuário autenticado pode
    listar e visualizar; apenas lojistas podem criar, editar e remover.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsLojista()]

class ProdutoViewSet(viewsets.ModelViewSet):
    """
    Gerencia produtos. Clientes e lojistas podem listar e visualizar;
    apenas lojistas podem criar, editar e remover seus próprios produtos.
    Suporta filtro por categoria e busca por nome/descrição.
    """
    serializer_class = ProdutoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria']
    search_fields = ['nome', 'descricao']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Lojista vê todos na listagem, mas só edita os seus. Cliente vê apenas ativos."""
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
    """
    Gerencia variações de produtos (tamanho, cor, estoque, preço).
    Todos os autenticados podem visualizar; apenas o lojista dono
    do produto pode criar, editar e remover variações.
    """
    serializer_class = VariacaoProdutoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsLojista()]

    def get_queryset(self):
        """Na edição/remoção, o lojista só acessa variações dos seus produtos."""
        user = self.request.user
        if user.tipo == 'lojista' and self.action not in ['list', 'retrieve']:
            return VariacaoProduto.objects.filter(produto__lojista=user)
        return VariacaoProduto.objects.all()

class UserViewSet(viewsets.ModelViewSet):
    """
    Permite que o usuário logado visualize e edite os próprios dados.
    Cada usuário só acessa suas próprias informações, nunca as de outros.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

class EnderecoViewSet(viewsets.ModelViewSet):
    """Gerencia os endereços do cliente logado."""
    serializer_class = EnderecoSerializer
    permission_classes = [IsCliente]

    def get_queryset(self):
        return Endereco.objects.filter(cliente=self.request.user)

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

class PagamentoViewSet(viewsets.ModelViewSet):
    """Gerencia os métodos de pagamento do cliente. Mascara dados sensíveis na resposta."""
    serializer_class = PagamentoSerializer
    permission_classes = [IsCliente]

    def get_queryset(self):
        return Pagamento.objects.filter(cliente=self.request.user)

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

class PedidoViewSet(viewsets.ModelViewSet):
    """
    Gerencia pedidos. Clientes finalizam compras e veem seus pedidos;
    lojistas veem os pedidos que contêm seus produtos e atualizam o status.
    """
    serializer_class = PedidoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

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
        """
        Finaliza a compra a partir do carrinho do cliente. Cria o pedido,
        os itens, baixa o estoque e esvazia o carrinho, tudo dentro de
        uma transação atômica para garantir consistência.
        """
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
        """Atualiza o status de um pedido. Restrito ao lojista."""
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
    """
    Exibe os itens de pedido. Cliente vê os itens dos seus pedidos;
    lojista vê os itens que contêm seus produtos. Somente leitura.
    """
    serializer_class = ItemPedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'lojista':
            return ItemPedido.objects.filter(variacao__produto__lojista=user)
        return ItemPedido.objects.filter(pedido__cliente=user)

class CarrinhoViewSet(viewsets.ModelViewSet):
    """
    Exibe o carrinho do cliente logado. Somente leitura — a manipulação
    de itens é feita pelo endpoint de itens do carrinho.
    """
    serializer_class = CarrinhoSerializer
    permission_classes = [IsCliente]

    def get_queryset(self):
        return Carrinho.objects.filter(cliente=self.request.user)

class ItemCarrinhoViewSet(viewsets.ModelViewSet):
    """
    Gerencia os itens do carrinho do cliente logado. Valida estoque
    e garante que o carrinho contenha produtos de um único lojista.
    """
    serializer_class = ItemCarrinhoSerializer
    permission_classes = [IsCliente]

    def get_queryset(self):
        carrinho = Carrinho.objects.get(cliente=self.request.user)
        return ItemCarrinho.objects.filter(carrinho=carrinho)

    def perform_create(self, serializer):
        carrinho = Carrinho.objects.get(cliente=self.request.user)
        serializer.save(carrinho=carrinho)