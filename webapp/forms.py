from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from webapp.models import *


class UsuarioswLoginForm(AuthenticationForm):
    class Meta:
        model = Usuariosw
        fields = ['username', 'password']


class UsuarioswCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuariosw
        fields = UserCreationForm.Meta.fields+('email', 'code_invitation')


class WalletForm(forms.ModelForm):
    class Meta:
        model = Usuariosw
        fields = ['wallet']


class BalanceRequestForm(forms.ModelForm):
    class Meta:
        model = BalanceRequest
        fields = ['amount', 'txid']


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = BalanceWithdrawal
        fields = ['amount', 'wallet_address']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(WithdrawalForm, self).__init__(*args, **kwargs)
        self.fields['wallet_address'].initial = user.wallet


class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }