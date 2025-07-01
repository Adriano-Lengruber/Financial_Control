from django.db import models
from django.conf import settings


class AnalyticsCache(models.Model):
    """Cache para resultados de análises pesadas."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cache_key = models.CharField(max_length=255)
    data = models.JSONField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_cache'
        unique_together = ['user', 'cache_key']
        indexes = [
            models.Index(fields=['user', 'cache_key']),
            models.Index(fields=['expires_at']),
        ]


class AnomalyDetection(models.Model):
    """Registro de anomalias detectadas."""
    
    ANOMALY_TYPES = [
        ('unusual_expense', 'Gasto Incomum'),
        ('budget_exceeded', 'Orçamento Excedido'),
        ('income_drop', 'Queda na Receita'),
        ('spending_spike', 'Pico de Gastos'),
        ('category_anomaly', 'Anomalia por Categoria'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='anomalies')
    anomaly_type = models.CharField(max_length=20, choices=ANOMALY_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    data = models.JSONField(default=dict)  # Dados específicos da anomalia
    is_resolved = models.BooleanField(default=False)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'anomaly_detections'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['user', 'is_resolved']),
            models.Index(fields=['user', 'anomaly_type']),
            models.Index(fields=['detected_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"


class Forecast(models.Model):
    """Previsões financeiras geradas."""
    
    FORECAST_TYPES = [
        ('balance', 'Saldo'),
        ('income', 'Receita'),
        ('expense', 'Despesa'),
        ('category', 'Por Categoria'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forecasts')
    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPES)
    target_date = models.DateField()
    predicted_value = models.DecimalField(max_digits=12, decimal_places=2)
    confidence_interval_lower = models.DecimalField(max_digits=12, decimal_places=2)
    confidence_interval_upper = models.DecimalField(max_digits=12, decimal_places=2)
    metadata = models.JSONField(default=dict)  # Metadados do modelo
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forecasts'
        ordering = ['target_date']
        indexes = [
            models.Index(fields=['user', 'forecast_type']),
            models.Index(fields=['user', 'target_date']),
        ]
    
    def __str__(self):
        return f"{self.get_forecast_type_display()} para {self.target_date}"
