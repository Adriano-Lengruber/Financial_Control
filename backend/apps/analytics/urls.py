from django.urls import path
from .views import (
    DashboardView,
    TransactionTrendsView,
    CategoryAnalysisView,
    AnomalyListView,
    ForecastView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('trends/', TransactionTrendsView.as_view(), name='transaction_trends'),
    path('categories/', CategoryAnalysisView.as_view(), name='category_analysis'),
    path('anomalies/', AnomalyListView.as_view(), name='anomalies'),
    path('forecast/', ForecastView.as_view(), name='forecast'),
]
