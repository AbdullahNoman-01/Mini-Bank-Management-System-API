from decimal import Decimal

from .import models
from rest_framework import serializers
class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BankAccount
        fields = ['id' , 'account_number', 'account_type', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'account_number', 'balance', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ['id', 'account', 'transaction_type', 'amount', 'description', 'created_at', 'updated_at']
        read_only_fields = fields 

class MoneyTransferSerializer(serializers.Serializer):
    receiver_account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    description = serializers.CharField(required=False, allow_blank=True)