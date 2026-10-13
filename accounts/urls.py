from django.urls import path
from .views import BankAccountListCreate_View, BankAccountDetailView, AccountBalanceView

urlpatterns = [
    path('accounts/', BankAccountListCreate_View.as_view(), name='bank_account_list_create'),
    path('accounts/<int:pk>/', BankAccountDetailView.as_view(), name='bank_account_detail'),
    path('accounts/<int:pk>/balance/', AccountBalanceView.as_view(), name='account_balance'),
]