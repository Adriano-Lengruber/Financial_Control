from django.contrib import admin
from .models import Category, Account, Transaction, RecurringTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'color', 'is_active', 'user', 'created_at']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    ordering = ['user', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'category_type')
        }),
        ('Aparência', {
            'fields': ('color', 'icon')
        }),
        ('Configurações', {
            'fields': ('is_active', 'user')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'balance', 'currency', 'is_active', 'user', 'created_at']
    list_filter = ['account_type', 'currency', 'is_active', 'created_at']
    search_fields = ['name', 'bank_name', 'account_number', 'user__email']
    ordering = ['user', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'account_type', 'balance', 'currency')
        }),
        ('Detalhes Bancários', {
            'fields': ('bank_name', 'account_number')
        }),
        ('Configurações', {
            'fields': ('is_active', 'user')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'transaction_type', 'category', 'account', 'date', 'status', 'user']
    list_filter = ['transaction_type', 'status', 'date', 'is_recurring', 'created_at']
    search_fields = ['title', 'description', 'notes', 'user__email']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'description', 'amount', 'transaction_type')
        }),
        ('Categorização', {
            'fields': ('category', 'account', 'destination_account')
        }),
        ('Data e Status', {
            'fields': ('date', 'status', 'is_recurring')
        }),
        ('Detalhes Adicionais', {
            'fields': ('tags', 'location', 'notes'),
            'classes': ('collapse',)
        }),
        ('Configurações', {
            'fields': ('user',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'category', 'account', 'destination_account'
        )


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'frequency', 'next_execution', 'is_active', 'user']
    list_filter = ['frequency', 'transaction_type', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'user__email']
    ordering = ['next_execution']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'next_execution'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'description', 'amount', 'transaction_type')
        }),
        ('Categorização', {
            'fields': ('category', 'account')
        }),
        ('Recorrência', {
            'fields': ('frequency', 'start_date', 'end_date', 'next_execution')
        }),
        ('Configurações', {
            'fields': ('is_active', 'user')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
