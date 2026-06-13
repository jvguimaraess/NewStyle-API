from rest_framework import serializers
from .models import Categoria, Produto, VariacaoProduto, Endereco, Pagamento, Pedido, ItemPedido, Carrinho, ItemCarrinho, User

class CategoriaSerializer(serializers.ModelSerializer):
    """Serializa categorias de produtos."""
    class Meta:
        model = Categoria
        fields = '__all__'

class ProdutoSerializer(serializers.ModelSerializer):
    """Serializa produtos. O lojista é preenchido automaticamente e não é editável."""
    class Meta:
        model = Produto
        fields = '__all__'
        read_only_fields = ['lojista', 'created_at']

class VariacaoProdutoSerializer(serializers.ModelSerializer):
    """Serializa variações de produto. Valida que estoque e preço não sejam negativos."""
    class Meta:
        model = VariacaoProduto
        fields = '__all__'

    def validate_estoque(self, value):
        if value < 0:
            raise serializers.ValidationError('O estoque não pode ser negativo.')
        return value

    def validate_preco(self, value):
        if value < 0:
            raise serializers.ValidationError('O preço não pode ser negativo.')
        return value

class EnderecoSerializer(serializers.ModelSerializer):
    """Serializa endereços."""
    class Meta:
        model = Endereco
        fields = '__all__'
        read_only_fields = ['cliente']

class PagamentoSerializer(serializers.ModelSerializer):
    """Serializa métodos de pagamento. Mascara os detalhes sensíveis na resposta."""
    detalhes_mascarado = serializers.SerializerMethodField()
    
    class Meta:
        model = Pagamento
        fields = ['id', 'tipo', 'detalhes', 'detalhes_mascarado', 'cliente']
        read_only_fields = ['cliente']
        extra_kwargs = {
            'detalhes': {'write_only': True}
        }

    def get_detalhes_mascarado(self, obj):
        if len(obj.detalhes) <= 4:
            return obj.detalhes
        return '*' * (len(obj.detalhes) - 4) + obj.detalhes[-4:]

class PedidoSerializer(serializers.ModelSerializer):
    """Serializa pedidos. Campos calculados e de controle são somente leitura."""
    class Meta:
        model = Pedido
        fields = '__all__'
        read_only_fields = ['cliente', 'total', 'status', 'created_at']
class ItemPedidoSerializer(serializers.ModelSerializer):
    """Serializa os itens de um pedido (somente leitura na API)."""
    class Meta:
        model = ItemPedido
        fields = '__all__'

class CarrinhoSerializer(serializers.ModelSerializer):
    """Serializa o carrinho do cliente (somente leitura na API)."""
    class Meta:
        model = Carrinho
        fields = '__all__'

class ItemCarrinhoSerializer(serializers.ModelSerializer):
    """
    Serializa itens do carrinho. Valida o estoque disponível e garante
    que o carrinho contenha produtos de um único lojista.
    """
    class Meta:
        model = ItemCarrinho
        fields = '__all__'
        read_only_fields = ['carrinho']

    def validate(self, data):
        variacao = data['variacao']
        quantidade = data['quantidade']

        if quantidade > variacao.estoque:
            raise serializers.ValidationError(
                'Quantidade maior que o estoque disponível.'
            )

        cliente = self.context['request'].user
        carrinho = Carrinho.objects.get(cliente=cliente)
        itens = carrinho.itens.all()

        if itens.exists():
            lojista_atual = itens.first().variacao.produto.lojista
            lojista_novo = variacao.produto.lojista
            if lojista_novo != lojista_atual:
                raise serializers.ValidationError(
                    'O carrinho só pode conter produtos de um único lojista.'
                )

        return data

class UserSerializer(serializers.ModelSerializer):
    """
    Serializa usuários. A senha é somente escrita (nunca retornada) e
    salva de forma criptografada no cadastro.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'tipo', 'created_at', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

