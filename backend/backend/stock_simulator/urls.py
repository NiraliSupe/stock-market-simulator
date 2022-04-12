from django.conf.urls import url, include
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from stock_simulator import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'cash-balance', views.CashBalanceViewSet, basename='cash_balance')
router.register(r'transaction', views.TransactionViewSet, basename='transaction')
router.register(r'stock', views.StockViewSet, basename='stock')
router.register(r'stockprice', views.StockPriceViewSet, basename='stockprice')
router.register(r'position', views.PositionViewSet, basename='position')
router.register(r'cash-transaction', views.CashTransactionViewSet, basename='cash_transaction')
router.register(r'evaluate', views.EvaluateAPIView, basename='evaluate')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('upload-trade/by-file', views.UploadTradeByFileAPIView.as_view()),
]
