from decimal import Decimal
from django.contrib.auth import get_user_model
User = get_user_model()
from .import models
from rest_framework import serializers
class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BankAccount
        fields = ['id' , 'account_number', 'account_type', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'account_number', 'balance', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(
        source='account.account_number',
        read_only=True
    )
    class Meta:
        model = models.Transaction
        fields = ['id', 'account', 'account_number', 'transaction_type', 'amount', 'description', 'created_at', 'updated_at']
        read_only_fields = fields 

class MoneyTransferSerializer(serializers.Serializer):
    receiver_account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    description = serializers.CharField(required=False, allow_blank=True)



class AdminCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'date_joined',]
        read_only_fields = fields

class AdminBankAccountSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(
        source='customer.username',
        read_only=True
    )
    class Meta:
        model = models.BankAccount
        fields = ['id',
            'customer',
            'customer_username',
            'account_number',
            'account_type',
            'balance',
            'created_at',
            'updated_at',]
        read_only_fields = fields