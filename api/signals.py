from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Carrinho

@receiver(post_save, sender=User)
def criar_carrinho(sender, instance, created, **kwargs):
    """Cria automaticamente um carrinho para cada novo usuário do tipo cliente."""
    if created and instance.tipo == 'cliente':
        Carrinho.objects.create(cliente=instance)