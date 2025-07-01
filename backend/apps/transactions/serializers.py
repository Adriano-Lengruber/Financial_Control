from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Account, Transaction, RecurringTransaction

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para categorias."""
    
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'color', 'icon', 
            'category_type', 'is_active', 'transaction_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'transaction_count']
    
    def get_transaction_count(self, obj):
        """Retorna o número de transações da categoria."""
        return obj.transactions.filter(user=self.context['request'].user).count()
    
    def validate_color(self, value):
        """Valida se a cor está em formato hexadecimal."""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Cor deve estar no formato hexadecimal (#RRGGBB)")
        return value


class AccountSerializer(serializers.ModelSerializer):
    """Serializer para contas."""
    
    balance_formatted = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'account_type', 'balance', 'balance_formatted',
            'currency', 'bank_name', 'account_number', 'is_active',
            'transaction_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance_formatted', 'transaction_count', 'created_at', 'updated_at']
    
    def get_balance_formatted(self, obj):
        """Retorna o saldo formatado como string."""
        return f"R$ {obj.balance:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def get_transaction_count(self, obj):
        """Retorna o número de transações da conta."""
        return obj.transactions.filter(user=self.context['request'].user).count()


class TransactionReadSerializer(serializers.ModelSerializer):
    """Serializer para leitura de transações."""
    
    category = CategorySerializer(read_only=True)
    account = AccountSerializer(read_only=True)
    destination_account = AccountSerializer(read_only=True)
    amount_formatted = serializers.SerializerMethodField()
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'description', 'amount', 'amount_formatted',
            'transaction_type', 'transaction_type_display', 'category', 
            'account', 'destination_account', 'date', 'status', 'status_display',
            'is_recurring', 'tags', 'location', 'notes',
            'created_at', 'updated_at'
        ]
    
    def get_amount_formatted(self, obj):
        """Retorna o valor formatado como string."""
        return f"R$ {obj.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


class TransactionWriteSerializer(serializers.ModelSerializer):
    """Serializer para criação/edição de transações."""
    
    class Meta:
        model = Transaction
        fields = [
            'title', 'description', 'amount', 'transaction_type',
            'category', 'account', 'destination_account', 'date',
            'status', 'is_recurring', 'tags', 'location', 'notes'
        ]
    
    def validate(self, data):
        """Validações customizadas."""
        # Validar transferência
        if data.get('transaction_type') == 'transfer' and not data.get('destination_account'):
            raise serializers.ValidationError({
                'destination_account': 'Transferências devem ter uma conta de destino.'
            })
        
        # Validar que a conta de destino é diferente da origem
        if (data.get('destination_account') and 
            data.get('account') == data.get('destination_account')):
            raise serializers.ValidationError({
                'destination_account': 'A conta de destino deve ser diferente da conta de origem.'
            })
        
        # Validar categoria compatível com tipo de transação
        category = data.get('category')
        transaction_type = data.get('transaction_type')
        if (category and transaction_type and 
            category.category_type not in ['both', transaction_type]):
            raise serializers.ValidationError({
                'category': 'Categoria incompatível com o tipo de transação.'
            })
        
        return data
    
    def create(self, validated_data):
        """Cria uma nova transação."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RecurringTransactionSerializer(serializers.ModelSerializer):
    """Serializer para transações recorrentes."""
    
    category = CategorySerializer(read_only=True)
    account = AccountSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    account_id = serializers.IntegerField(write_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = RecurringTransaction
        fields = [
            'id', 'title', 'description', 'amount', 'transaction_type',
            'transaction_type_display', 'category', 'category_id', 
            'account', 'account_id', 'frequency', 'frequency_display',
            'start_date', 'end_date', 'next_execution', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'next_execution', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Cria uma nova transação recorrente."""
        validated_data['user'] = self.context['request'].user
        validated_data['next_execution'] = validated_data['start_date']
        return super().create(validated_data)


class TransactionSummarySerializer(serializers.Serializer):
    """Serializer para resumo de transações."""
    
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transfer = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
    period_start = serializers.DateField()
    period_end = serializers.DateField()


class CategorySummarySerializer(serializers.Serializer):
    """Serializer para resumo por categoria."""
    
    category = CategorySerializer()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
