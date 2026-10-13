from django.urls import path
from .views import BankAccountListCreate_View, BankAccountDetailView, AccountBalanceView, DepositView, TransactionHistoryView, WithdrawalView

urlpatterns = [
    path('accounts/', BankAccountListCreate_View.as_view(), name='bank_account_list_create'),
    path('accounts/<int:pk>/', BankAccountDetailView.as_view(), name='bank_account_detail'),
    path('accounts/<int:pk>/balance/', AccountBalanceView.as_view(), name='account_balance'),

    path('accounts/<int:pk>/deposit/',DepositView.as_view(),name='account-deposit'),
    path('accounts/<int:pk>/withdraw/',WithdrawalView.as_view(),name='account-withdraw'),
    path('accounts/<int:pk>/transactions/', TransactionHistoryView.as_view(),name='account-transactions'),
]