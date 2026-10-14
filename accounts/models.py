from django.db import models
from django.conf import settings
import secrets

# Create your models here.
class TimestampedModel(models.Model):
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      abstract = True   



class BankAccount(TimestampedModel):
   Account_type = [
      ('SAVINGS', 'Savings'),
      ('CURRENT', 'Current'),
   ]
   customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='bank_accounts')
   account_number = models.CharField(max_length=20, unique=True)
   account_type = models.CharField(max_length=10, choices=Account_type)
   balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

   
   def save(self, *args, **kwargs):
      if not self.account_number:
         while True:
            number = secrets.randbelow(9000000000) + 1000000000
            account_number = str(number)
            if not BankAccount.objects.filter(
                account_number=account_number
            ).exists():
                self.account_number = account_number
                break

      super().save(*args, **kwargs)


   def __str__(self):
      return f"{self.customer.username} - {self.account_number}"


class Transaction(TimestampedModel):
   DEPOSIT = 'DEPOSIT'
   WITHDRAWAL = 'WITHDRAWAL'
   TRANSACTION_TYPE = [
      ('DEPOSIT', 'Deposit'),
      ('WITHDRAWAL', 'Withdrawal'),
      ('TRANSFER_OUT', 'Transfer Sent'),
      ('TRANSFER_IN', 'Transfer Received'),
   ]
   account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
   transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPE)
   amount = models.DecimalField(max_digits=12, decimal_places=2,default=0.00)
   description = models.TextField(blank=True, null=True)

   def __str__(self):
      return f"{self.transaction_type} - {self.amount} - {self.account.account_number}"                  