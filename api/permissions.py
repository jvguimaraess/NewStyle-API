from rest_framework.permissions import BasePermission

class IsLojista(BasePermission):
    """Permite acesso apenas a usuários autenticados do tipo lojista."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo == 'lojista'

class IsCliente(BasePermission):
    """Permite acesso apenas a usuários autenticados do tipo cliente."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo == 'cliente'

