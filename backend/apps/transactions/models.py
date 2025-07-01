from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Categorias para classificar transações."""
    
    CATEGORY_TYPES = [
        ('income', 'Receita'),
        ('expense', 'Despesa'),
        ('both', 'Ambos'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    color = models.CharField(max_length=7, default='#6B7280', verbose_name='Cor')  # Hex color
    icon = models.CharField(max_length=50, blank=True, verbose_name='Ícone')
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, verbose_name='Tipo')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return self.name


class Account(models.Model):
    """Contas bancárias ou carteiras do usuário."""
    
    ACCOUNT_TYPES = [
        ('checking', 'Conta Corrente'),
        ('savings', 'Poupança'),
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('cash', 'Dinheiro'),
        ('investment', 'Investimento'),
        ('other', 'Outros'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nome')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name='Tipo')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Saldo')
    currency = models.CharField(max_length=3, default='BRL', verbose_name='Moeda')
    bank_name = models.CharField(max_length=100, blank=True, verbose_name='Banco')
    account_number = models.CharField(max_length=50, blank=True, verbose_name='Número da Conta')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.get_account_type_display()}"

    def update_balance(self, amount):
        """Atualiza o saldo da conta."""
        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])


class Transaction(models.Model):
    """Transações financeiras do usuário."""
    
    TRANSACTION_TYPES = [
        ('income', 'Receita'),
        ('expense', 'Despesa'),
        ('transfer', 'Transferência'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pendente'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descrição')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name='Tipo')
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='transactions',
        verbose_name='Categoria'
    )
    account = models.ForeignKey(
        Account, 
        on_delete=models.PROTECT, 
        related_name='transactions',
        verbose_name='Conta'
    )
    destination_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='received_transfers',
        null=True,
        blank=True,
        verbose_name='Conta Destino'
    )
    date = models.DateField(verbose_name='Data')
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='completed', verbose_name='Status')
    is_recurring = models.BooleanField(default=False, verbose_name='Recorrente')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    
    # Campos para análise e ML
    tags = models.JSONField(default=list, blank=True, verbose_name='Tags')
    location = models.CharField(max_length=200, blank=True, verbose_name='Local')
    notes = models.TextField(blank=True, verbose_name='Observações')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'account']),
        ]

    def __str__(self):
        return f"{self.title} - R$ {self.amount} ({self.get_transaction_type_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validar transferência
        if self.transaction_type == 'transfer' and not self.destination_account:
            raise ValidationError('Transferências devem ter uma conta de destino.')
        
        # Validar que a conta de destino é diferente da origem
        if self.destination_account and self.account == self.destination_account:
            raise ValidationError('A conta de destino deve ser diferente da conta de origem.')
        
        # Validar categoria compatível com tipo de transação
        if self.category and self.category.category_type not in ['both', self.transaction_type]:
            raise ValidationError('Categoria incompatível com o tipo de transação.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RecurringTransaction(models.Model):
    """Template para transações recorrentes."""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descrição')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor')
    transaction_type = models.CharField(max_length=10, choices=Transaction.TRANSACTION_TYPES, verbose_name='Tipo')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Categoria')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name='Conta')
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, verbose_name='Frequência')
    start_date = models.DateField(verbose_name='Data de Início')
    end_date = models.DateField(null=True, blank=True, verbose_name='Data de Fim')
    next_execution = models.DateField(verbose_name='Próxima Execução')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_transactions')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recurring_transactions'
        verbose_name = 'Transação Recorrente'
        verbose_name_plural = 'Transações Recorrentes'
        ordering = ['next_execution']

    def __str__(self):
        return f"{self.title} - {self.get_frequency_display()}"
