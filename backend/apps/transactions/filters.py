import django_filters
from django.db.models import Q
from .models import Transaction, Category, Account


class TransactionFilter(django_filters.FilterSet):
    """Filtros para transações."""
    
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    amount_from = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_to = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.none(),
        field_name='category',
        to_field_name='id'
    )
    
    account = django_filters.ModelMultipleChoiceFilter(
        queryset=Account.objects.none(),
        field_name='account',
        to_field_name='id'
    )
    
    transaction_type = django_filters.MultipleChoiceFilter(
        choices=Transaction.TRANSACTION_TYPES,
        field_name='transaction_type'
    )
    
    status = django_filters.MultipleChoiceFilter(
        choices=Transaction.TRANSACTION_STATUS,
        field_name='status'
    )
    
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_type', 'status', 'is_recurring',
            'date_from', 'date_to', 'amount_from', 'amount_to',
            'category', 'account', 'search'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.request:
            user = self.request.user
            self.filters['category'].queryset = Category.objects.filter(user=user, is_active=True)
            self.filters['account'].queryset = Account.objects.filter(user=user, is_active=True)
    
    def filter_search(self, queryset, name, value):
        """Filtro de busca personalizado."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(notes__icontains=value) |
            Q(location__icontains=value)
        )
