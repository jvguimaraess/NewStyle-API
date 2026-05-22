from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Categoria, Produto, VariacaoProduto, Pedido, ItemPedido, Carrinho, ItemCarrinho

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'tipo', 'is_staff']
    search_fields = ['email', 'username']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(VariacaoProduto)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(Carrinho)
admin.site.register(ItemCarrinho)