from rest_framework import serializers
from .models import Categoria, Produto, VariacaoProduto, Pedido, ItemPedido, Carrinho, ItemCarrinho, User

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'
        read_only_fields = ['lojista', 'created_at']

class VariacaoProdutoSerializer(serializers.ModelSerializer):
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

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'

class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = '__all__'

class CarrinhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrinho
        fields = '__all__'

class ItemCarrinhoSerializer(serializers.ModelSerializer):
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

