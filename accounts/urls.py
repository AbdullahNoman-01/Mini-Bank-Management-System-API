from django.urls import path
from .views import BankAccountListCreate_View, BankAccountDetailView, AccountBalanceView, DepositView, TransactionHistoryView, WithdrawalView, MoneyTransferView, AdminCustomerListView, AdminBankAccountListView, AdminTransactionListView

urlpatterns = [
    path('accounts/', BankAccountListCreate_View.as_view(), name='bank_account_list_create'),
    path('accounts/<int:pk>/', BankAccountDetailView.as_view(), name='bank_account_detail'),
    path('accounts/<int:pk>/balance/', AccountBalanceView.as_view(), name='account_balance'),

    path('accounts/<int:pk>/deposit/',DepositView.as_view(),name='account-deposit'),
    path('accounts/<int:pk>/withdraw/',WithdrawalView.as_view(),name='account-withdraw'),
    path('accounts/<int:pk>/transactions/', TransactionHistoryView.as_view(),name='account-transactions'),
    path('accounts/<int:sender_account_id>/transfer/',MoneyTransferView.as_view(),name='money-transfer'),

    path('admin/customers/',AdminCustomerListView.as_view(),name='admin-customers'),
    path('admin/accounts/',AdminBankAccountListView.as_view(),name='admin-bank-accounts'),
    path('admin/transactions/',AdminTransactionListView.as_view(),name='admin-transactions'),
]