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