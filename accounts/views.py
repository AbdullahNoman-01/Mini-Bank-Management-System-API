from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import BankAccount
from accounts.serializers import BankAccountSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


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


