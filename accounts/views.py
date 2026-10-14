from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import BankAccount, Transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .import serializers
from rest_framework import status
from django.db import transaction
from .serializers import TransactionSerializer
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser
from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError
from accounts.serializers import BankAccountSerializer, MoneyTransferSerializer,        AdminBankAccountSerializer,AdminCustomerSerializer


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

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transaction_type']

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            account__customer=self.request.user).select_related('account').order_by('-created_at')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        parsed_start = None
        parsed_end = None

        if start_date:
            parsed_start = parse_date(start_date)
            if parsed_start is None:
                raise ValidationError({
                    'start_date': 'Use YYYY-MM-DD format.'
                })
        if end_date:
            parsed_end = parse_date(end_date)
            if parsed_end is None:
                raise ValidationError({
                    'end_date': 'Use YYYY-MM-DD format.'
                })
        if parsed_start and parsed_end and parsed_start > parsed_end:
            raise ValidationError({
                'detail': 'start_date cannot be after end_date.'
            })
        if parsed_start:
            queryset = queryset.filter(
                created_at__date__gte=parsed_start
            )
        if parsed_end:
            queryset = queryset.filter(
                created_at__date__lte=parsed_end
            )
        return queryset

    



class MoneyTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, sender_account_id):
        serializer = MoneyTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receiver_number = serializer.validated_data[
            'receiver_account_number'
        ]
        amount = serializer.validated_data['amount']

        with transaction.atomic():

            # 1. Sender-er nijer account kina verify kora
            sender_exists = BankAccount.objects.filter(
                id=sender_account_id,
                customer=request.user
            ).exists()

            if not sender_exists:
                return Response(
                    {'detail': 'Sender account not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 2. Receiver account khuje ber kora
            receiver_id = BankAccount.objects.filter(
                account_number=receiver_number
            ).values_list('id', flat=True).first()

            if receiver_id is None:
                return Response(
                    {'detail': 'Receiver account not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 3. Same account-e transfer bondho kora
            if sender_account_id == receiver_id:
                return Response(
                    {
                        'detail': (
                            'Cannot transfer money to the same account.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 4. Dui account ID order onujayi lock kora
            locked_accounts = {
                account.id: account
                for account in (
                    BankAccount.objects.select_for_update()
                    .filter(
                        id__in=[sender_account_id, receiver_id]
                    )
                    .order_by('id')
                )
            }

            sender_account = locked_accounts.get(sender_account_id)
            receiver_account = locked_accounts.get(receiver_id)

            if sender_account is None or receiver_account is None:
                return Response(
                    {'detail': 'Account not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 5. Sender-er balance check kora
            if sender_account.balance < amount:
                return Response(
                    {
                        'detail': 'Insufficient balance.',
                        'available_balance': str(
                            sender_account.balance
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 6. Dui account-er balance update kora
            sender_account.balance -= amount
            receiver_account.balance += amount

            sender_account.save(update_fields=['balance'])
            receiver_account.save(update_fields=['balance'])

            # 7. Sender-er transaction history
            Transaction.objects.create(
                account=sender_account,
                transaction_type='TRANSFER_OUT',
                amount=amount,
                description=(
                    f'Transfer to account '
                    f'{receiver_account.account_number}'
                )
            )

            # 8. Receiver-er transaction history
            Transaction.objects.create(
                account=receiver_account,
                transaction_type='TRANSFER_IN',
                amount=amount,
                description=(
                    f'Transfer from account '
                    f'{sender_account.account_number}'
                )
            )

        # 9. Success response
        return Response(
            {
                'message': 'Money transferred successfully.',
                'amount': str(amount),
                'sender_account': sender_account.account_number,
                'sender_balance': str(sender_account.balance),
                'receiver_account': receiver_account.account_number,
                'receiver_balance': str(receiver_account.balance),
            },
            status=status.HTTP_200_OK
        )




User = get_user_model()


class AdminCustomerListView(ListAPIView):
    serializer_class = AdminCustomerSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(
            is_staff=False,
            is_superuser=False
        ).order_by('id')


class AdminBankAccountListView(ListAPIView):
    serializer_class = AdminBankAccountSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return BankAccount.objects.select_related(
            'customer'
        ).order_by('-created_at')


class AdminTransactionListView(ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Transaction.objects.select_related(
            'account',
            'account__customer'
        ).order_by('-created_at')