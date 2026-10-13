from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import BankAccount, Transaction
from accounts.serializers import BankAccountSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .import serializers
from rest_framework import status
from django.db import transaction
from .serializers import TransactionSerializer
from rest_framework import serializers
from rest_framework.generics import ListAPIView

# Create your views here.
class BankAccountListCreate_View(generics.ListCreateAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(
            customer=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class BankAccountDetailView(generics.RetrieveAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(
            customer=self.request.user
        )


class AccountBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        account = get_object_or_404(
            BankAccount,
            pk=pk,
            customer=request.user
        )

        return Response({
            'account_number': account.account_number,
            'balance': account.balance,
        })




class MoneyRequestSerializer(serializers.Serializer):
      amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
      description = serializers.CharField(max_length=255, required=False, allow_blank=True)



class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = MoneyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        with transaction.atomic():
            try:
                account = BankAccount.objects.select_for_update().get(
                    pk=pk,
                    customer=request.user
                )
            except BankAccount.DoesNotExist:
                return Response(
                    {'detail': 'Account not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            account.balance += amount
            account.save(update_fields=['balance'])

            record = Transaction.objects.create(
                account=account,
                transaction_type=Transaction.DEPOSIT,
                amount=amount
            )

        return Response({
            'message': 'Deposit successful.',
            'account_id': account.id,
            'amount': str(record.amount),
            'balance': str(account.balance),
            'transaction': TransactionSerializer(record).data
        }, status=status.HTTP_200_OK)


class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = MoneyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        with transaction.atomic():
            try:
                account = BankAccount.objects.select_for_update().get(
                    pk=pk,
                    customer=request.user
                )
            except BankAccount.DoesNotExist:
                return Response(
                    {'detail': 'Account not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if account.balance < amount:
                return Response({
                    'detail': 'Insufficient balance.',
                    'available_balance': str(account.balance)
                }, status=status.HTTP_400_BAD_REQUEST)

            account.balance -= amount
            account.save(update_fields=['balance'])

            record = Transaction.objects.create(
                account=account,
                transaction_type=Transaction.WITHDRAWAL,
                amount=amount
            )

        return Response({
            'message': 'Withdrawal successful.',
            'account_id': account.id,
            'amount': str(record.amount),
            'balance': str(account.balance),
            'transaction': TransactionSerializer(record).data
        }, status=status.HTTP_200_OK)


class TransactionHistoryView(ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            account__customer=self.request.user
        ).select_related('account').order_by('-created_at')