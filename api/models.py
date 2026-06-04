from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    TIPO_CHOICES = [
        ('lojista', 'Lojista'),
        ('cliente', 'Cliente'),
    ]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'tipo']

    email = models.EmailField(unique=True, null=False, blank=False)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Categoria(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    lojista = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produtos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos')
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class VariacaoProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='variacoes')
    tamanho = models.CharField(max_length=15)
    cor = models.CharField(max_length=15)
    estoque = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produto.nome} - {self.tamanho} - {self.cor}"

class Endereco(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enderecos')
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return f'{self.rua}, {self.numero} - {self.cidade}/{self.estado}'

class Pagamento(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagamentos')

    TIPO_CHOICES = [
        ('cartao', 'Cartão'),
        ('pix', 'Pix'),
        ('boleto', 'Boleto'),
    ]

    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    detalhes = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.tipo} - {self.cliente.email}'

class Pedido(models.Model):

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    endereco = models.ForeignKey(Endereco, on_delete=models.PROTECT, null=True)
    pagamento = models.ForeignKey(Pagamento, on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.email}'

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    variacao = models.ForeignKey(VariacaoProduto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantidade} x {self.variacao}'

class Carrinho(models.Model):
    cliente = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrinho')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Carrinho de {self.cliente.email}'

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    variacao = models.ForeignKey(VariacaoProduto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('carrinho', 'variacao')

    def __str__(self):
        return f'{self.quantidade} x {self.variacao}'
