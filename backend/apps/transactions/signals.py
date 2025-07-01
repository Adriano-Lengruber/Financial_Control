from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Category, Transaction

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    """Cria categorias padrão para novos usuários."""
    if created:
        default_categories = [
            # Receitas
            {'name': 'Salário', 'category_type': 'income', 'color': '#10B981', 'icon': 'briefcase'},
            {'name': 'Freelance', 'category_type': 'income', 'color': '#3B82F6', 'icon': 'computer'},
            {'name': 'Investimentos', 'category_type': 'income', 'color': '#8B5CF6', 'icon': 'chart-bar'},
            {'name': 'Outros Rendimentos', 'category_type': 'income', 'color': '#06B6D4', 'icon': 'cash'},
            
            # Despesas
            {'name': 'Alimentação', 'category_type': 'expense', 'color': '#EF4444', 'icon': 'cutlery'},
            {'name': 'Transporte', 'category_type': 'expense', 'color': '#F59E0B', 'icon': 'car'},
            {'name': 'Moradia', 'category_type': 'expense', 'color': '#84CC16', 'icon': 'home'},
            {'name': 'Saúde', 'category_type': 'expense', 'color': '#EC4899', 'icon': 'heart'},
            {'name': 'Educação', 'category_type': 'expense', 'color': '#6366F1', 'icon': 'academic-cap'},
            {'name': 'Lazer', 'category_type': 'expense', 'color': '#F97316', 'icon': 'puzzle'},
            {'name': 'Compras', 'category_type': 'expense', 'color': '#14B8A6', 'icon': 'shopping-bag'},
            {'name': 'Contas', 'category_type': 'expense', 'color': '#64748B', 'icon': 'document-text'},
            
            # Ambos
            {'name': 'Transferência', 'category_type': 'both', 'color': '#6B7280', 'icon': 'arrow-right'},
        ]
        
        for cat_data in default_categories:
            Category.objects.create(user=instance, **cat_data)


@receiver(post_save, sender=User)
def create_default_accounts(sender, instance, created, **kwargs):
    """Cria contas padrão para novos usuários."""
    if created:
        from .models import Account
        
        default_accounts = [
            {'name': 'Conta Corrente', 'account_type': 'checking'},
            {'name': 'Poupança', 'account_type': 'savings'},
            {'name': 'Carteira', 'account_type': 'cash'},
        ]
        
        for acc_data in default_accounts:
            Account.objects.create(user=instance, **acc_data)


@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    """Atualiza saldo da conta quando uma transação é salva."""
    if instance.status == 'completed' and created:
        # A lógica de atualização já está na ViewSet
        pass


@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    """Atualiza saldo da conta quando uma transação é excluída."""
    if instance.status == 'completed':
        # A lógica de reversão já está na ViewSet
        pass
