from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import datetime, timedelta
from django.utils import timezone


class Usuariosw(AbstractUser):
    code_reference = models.CharField(max_length=10, unique=True)
    code_invitation = models.CharField(max_length=10)
    wallet = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='wallet')
    Balance = models.FloatField(null=True, default=0, verbose_name='balance')

    def save(self, *args, **kwargs):
        if not self.code_reference:
            self.code_reference = str(uuid.uuid4())[:10]
        super().save(*args, **kwargs)

    @property
    def referral_count(self):
        return Usuariosw.objects.filter(code_invitation=self.code_reference).count()


class BalanceRequest(models.Model):
    user = models.ForeignKey(Usuariosw, on_delete=models.CASCADE)
    amount = models.FloatField(default=10)
    txid = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='txid')
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usuario: {self.user.username} - Amount: {self.amount} - txid: {self.txid} - ¿Aproved? {self.approved}"

    @classmethod
    def total_approved_recharges(cls):
        return cls.objects.filter(approved=True).aggregate(total=models.Sum('amount'))['total'] or 0


class BalanceWithdrawal(models.Model):
    user = models.ForeignKey(Usuariosw, on_delete=models.CASCADE)
    amount = models.FloatField(default=10)
    wallet_address = models.CharField(max_length=100, verbose_name='Wallet Address')
    txid = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='Transaction ID')
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usuario: {self.user.username} - Amount: {self.amount} - Wallet: {self.wallet_address} - txid: {self.txid} - ¿Approved? {self.approved}"

    @classmethod
    def total_approved_withdrawals(cls):
        return cls.objects.filter(approved=True).aggregate(total=models.Sum('amount'))['total'] or 0


class Vips(models.Model):
    price = models.FloatField(null=False, verbose_name='price')

    @property
    def dreward(self):
        if self.price <= 30:
            return round((self.price * 0.05), 2)
        elif 31 <= self.price <= 100:
            return round((self.price * 0.055), 2)
        elif 101 <= self.price <= 500:
            return round((self.price * 0.06), 2)
        elif 501 <= self.price <= 1000:
            return round((self.price * 0.065), 2)
        elif 1001 <= self.price <= 3000:
            return round((self.price * 0.07), 2)
        elif 3001 <= self.price <= 5000:
            return round((self.price * 0.1), 2)

    def __str__(self):
        return f"Vip: {self.id} - ${self.price} - Daily reward: {self.dreward}"


class Purchase(models.Model):
    user = models.ForeignKey(Usuariosw, on_delete=models.CASCADE)
    vip = models.ForeignKey(Vips, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    reward_count = models.PositiveIntegerField(default=0)
    last_claimed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} purchased {self.vip.id} - ${self.vip.price} on {self.purchase_date}"


class HelpRequest(models.Model):
    user = models.ForeignKey(Usuariosw, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.created_at}'



