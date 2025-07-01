from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Category, Account, Transaction, RecurringTransaction
from .serializers import (
    CategorySerializer, AccountSerializer, 
    TransactionReadSerializer, TransactionWriteSerializer,
    RecurringTransactionSerializer, TransactionSummarySerializer,
    CategorySummarySerializer
)
from .filters import TransactionFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar categorias."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        return CategorySerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Retorna categorias filtradas por tipo."""
        category_type = request.query_params.get('type')
        if not category_type:
            return Response({'error': 'Parâmetro type é obrigatório'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(
            Q(category_type=category_type) | Q(category_type='both')
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar contas."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bank_name']
    ordering_fields = ['name', 'balance', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        return AccountSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def adjust_balance(self, request, pk=None):
        """Ajusta o saldo da conta."""
        account = self.get_object()
        try:
            new_balance = Decimal(str(request.data.get('balance', 0)))
            account.balance = new_balance
            account.save(update_fields=['balance', 'updated_at'])
            
            serializer = self.get_serializer(account)
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response({'error': 'Valor inválido para o saldo'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Retorna resumo das contas."""
        accounts = self.get_queryset()
        total_balance = accounts.aggregate(total=Sum('balance'))['total'] or Decimal('0')
        
        return Response({
            'total_accounts': accounts.count(),
            'total_balance': total_balance,
            'accounts_by_type': accounts.values('account_type').annotate(
                count=Count('id'),
                total_balance=Sum('balance')
            )
        })


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar transações."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['title', 'description', 'notes']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related(
            'category', 'account', 'destination_account'
        )
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TransactionWriteSerializer
        return TransactionReadSerializer
    
    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        self._update_account_balances(transaction)
    
    def perform_update(self, serializer):
        old_transaction = self.get_object()
        # Reverter operação anterior
        self._revert_account_balances(old_transaction)
        
        # Aplicar nova operação
        transaction = serializer.save()
        self._update_account_balances(transaction)
    
    def perform_destroy(self, instance):
        self._revert_account_balances(instance)
        instance.delete()
    
    def _update_account_balances(self, transaction):
        """Atualiza os saldos das contas baseado na transação."""
        if transaction.status != 'completed':
            return
        
        if transaction.transaction_type == 'income':
            transaction.account.update_balance(transaction.amount)
        elif transaction.transaction_type == 'expense':
            transaction.account.update_balance(-transaction.amount)
        elif transaction.transaction_type == 'transfer':
            transaction.account.update_balance(-transaction.amount)
            if transaction.destination_account:
                transaction.destination_account.update_balance(transaction.amount)
    
    def _revert_account_balances(self, transaction):
        """Reverte os saldos das contas baseado na transação."""
        if transaction.status != 'completed':
            return
        
        if transaction.transaction_type == 'income':
            transaction.account.update_balance(-transaction.amount)
        elif transaction.transaction_type == 'expense':
            transaction.account.update_balance(transaction.amount)
        elif transaction.transaction_type == 'transfer':
            transaction.account.update_balance(transaction.amount)
            if transaction.destination_account:
                transaction.destination_account.update_balance(-transaction.amount)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Retorna resumo das transações por período."""
        start_date = parse_date(request.query_params.get('start_date', ''))
        end_date = parse_date(request.query_params.get('end_date', ''))
        
        if not start_date:
            start_date = datetime.now().date().replace(day=1)
        if not end_date:
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        
        queryset = self.get_queryset().filter(
            date__gte=start_date,
            date__lte=end_date,
            status='completed'
        )
        
        summary = queryset.aggregate(
            total_income=Sum('amount', filter=Q(transaction_type='income')) or Decimal('0'),
            total_expense=Sum('amount', filter=Q(transaction_type='expense')) or Decimal('0'),
            total_transfer=Sum('amount', filter=Q(transaction_type='transfer')) or Decimal('0'),
            transaction_count=Count('id')
        )
        
        summary['balance'] = summary['total_income'] - summary['total_expense']
        summary['period_start'] = start_date
        summary['period_end'] = end_date
        
        serializer = TransactionSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Retorna resumo das transações por categoria."""
        start_date = parse_date(request.query_params.get('start_date', ''))
        end_date = parse_date(request.query_params.get('end_date', ''))
        transaction_type = request.query_params.get('type', 'expense')
        
        if not start_date:
            start_date = datetime.now().date().replace(day=1)
        if not end_date:
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        
        queryset = self.get_queryset().filter(
            date__gte=start_date,
            date__lte=end_date,
            transaction_type=transaction_type,
            status='completed'
        )
        
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        category_summary = queryset.values('category').annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('-total_amount')
        
        results = []
        for item in category_summary:
            category = Category.objects.get(id=item['category'])
            percentage = (item['total_amount'] / total_amount * 100) if total_amount > 0 else 0
            
            results.append({
                'category': CategorySerializer(category).data,
                'total_amount': item['total_amount'],
                'transaction_count': item['transaction_count'],
                'percentage': round(percentage, 2)
            })
        
        return Response(results)


class RecurringTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar transações recorrentes."""
    
    serializer_class = RecurringTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['next_execution', 'created_at']
    ordering = ['next_execution']
    
    def get_queryset(self):
        return RecurringTransaction.objects.filter(
            user=self.request.user, 
            is_active=True
        ).select_related('category', 'account')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Executa uma transação recorrente."""
        recurring = self.get_object()
        
        # Criar a transação
        transaction = Transaction.objects.create(
            title=recurring.title,
            description=recurring.description,
            amount=recurring.amount,
            transaction_type=recurring.transaction_type,
            category=recurring.category,
            account=recurring.account,
            date=datetime.now().date(),
            user=recurring.user
        )
        
        # Atualizar próxima execução
        self._update_next_execution(recurring)
        
        return Response({
            'message': 'Transação executada com sucesso',
            'transaction_id': transaction.id
        })
    
    def _update_next_execution(self, recurring):
        """Atualiza a data da próxima execução."""
        current_date = recurring.next_execution
        
        if recurring.frequency == 'daily':
            next_date = current_date + timedelta(days=1)
        elif recurring.frequency == 'weekly':
            next_date = current_date + timedelta(weeks=1)
        elif recurring.frequency == 'monthly':
            next_date = current_date + timedelta(days=30)  # Aproximação
        elif recurring.frequency == 'quarterly':
            next_date = current_date + timedelta(days=90)  # Aproximação
        elif recurring.frequency == 'yearly':
            next_date = current_date + timedelta(days=365)  # Aproximação
        else:
            next_date = current_date + timedelta(days=30)
        
        recurring.next_execution = next_date
        recurring.save(update_fields=['next_execution', 'updated_at'])
