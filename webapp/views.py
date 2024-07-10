from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404

from webapp.forms import *
from webapp.models import *


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'home.html')


def login_users(request):
    if request.method == 'POST':
        form = UsuarioswLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Incorrect username or password")
        else:
            messages.error(request, "Incorrect username or password")
    else:
        form = UsuarioswLoginForm()
    return render(request, 'loger/login_users.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UsuarioswCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
        else:
            errors = form.errors.as_data()
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UsuarioswCreationForm()
    return render(request, 'loger/register.html', {'form': form})


@login_required
def update_wallet(request):
    if request.method == 'POST':
        formWallet = WalletForm(request.POST, instance=request.user)
        if formWallet.is_valid():
            formWallet.save()
            messages.success(request, 'Your wallet has been successfully updated.')
            return redirect('dashboard')


@login_required
def request_balance(request):
    if request.method == 'POST':
        form = BalanceRequestForm(request.POST)
        if form.is_valid():
            balance_request = form.save(commit=False)
            balance_request.user = request.user
            balance_request.save()
            return redirect('dashboard')


@login_required
def approve_balance_request(request, request_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    balance_request = BalanceRequest.objects.get(id=request_id)
    balance_request.approved = True
    balance_request.save()
    user = balance_request.user
    user.Balance += balance_request.amount
    user.save()
    return redirect('dashboard')


@login_required
def delete_balance_request(request, request_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    balance_request = get_object_or_404(BalanceRequest, id=request_id)
    balance_request.delete()
    return redirect('dashboard')


@login_required
def request_withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST, user=request.user)
        if form.is_valid():
            withdrawal_request = form.save(commit=False)
            withdrawal_request.user = request.user

            if request.user.Balance >= withdrawal_request.amount:
                request.user.Balance -= withdrawal_request.amount
                request.user.save()
                withdrawal_request.save()
                return redirect('dashboard')
            else:
                form.add_error('amount', 'Insufficient balance')


@login_required
def approve_withdrawal(request, req_id):
    withdrawal_request = get_object_or_404(BalanceWithdrawal, id=req_id)
    if request.method == 'POST':
        withdrawal_request.approved = True
        withdrawal_request.txid = request.POST.get('txid')
        withdrawal_request.save()
        return redirect('dashboard')


@login_required
def dashboard(request):
    total_approved_recharges = BalanceRequest.total_approved_recharges()
    total_approved_withdrawals = BalanceWithdrawal.total_approved_withdrawals()
    vips = Vips.objects.all()
    requests = BalanceRequest.objects.all()
    withdrawal_requests = BalanceWithdrawal.objects.all()
    purchased_vips = Purchase.objects.filter(user=request.user).values_list('vip_id', flat=True)
    purchase_by_vip_id = {purchase.vip_id: purchase for purchase in Purchase.objects.filter(user=request.user)}

    time_remaining = None
    if purchased_vips:
        vip_id = purchased_vips[0]
        purchase = Purchase.objects.filter(user=request.user, vip_id=vip_id).first()
        if purchase and purchase.last_claimed:
            time_remaining = (purchase.last_claimed + timedelta(hours=24)) - timezone.now()
            time_remaining = time_remaining.total_seconds()

        # Añadir la lógica para calcular el tiempo restante
    for purchase in purchase_by_vip_id.values():
        if purchase.last_claimed and (timezone.now() - purchase.last_claimed) < timedelta(hours=24):
            purchase.time_remaining = timedelta(hours=24) - (timezone.now() - purchase.last_claimed)

    context = {
        'vips': vips,
        'purchased_vips': purchased_vips,
        'time_remaining': time_remaining,
        'requests': requests,
        'withdrawal_requests': withdrawal_requests,
        'total_approved_recharges': total_approved_recharges,
        'total_approved_withdrawals': total_approved_withdrawals,
        'purchase_by_vip_id': purchase_by_vip_id,
    }
    return render(request, 'homeusers/dashboard.html', context)


@login_required
def comprar_vip(request, vip_id):
    vip = get_object_or_404(Vips, id=vip_id)
    user = request.user

    # Verificar si el usuario ya ha comprado este VIP
    if Purchase.objects.filter(user=user, vip=vip).exists():
        messages.error(request, "Ya has comprado este VIP.")
        return redirect('dashboard')

    # Realizar la compra
    purchase = Purchase(user=user, vip=vip)
    purchase.save()

    # Deduct the VIP price from the user's balance
    user.Balance -= vip.price
    user.save()

    # Obtener el usuario del código de invitación y sumar 10% del precio del VIP a su balance
    if user.code_invitation:
        invitador = Usuariosw.objects.filter(code_reference=user.code_invitation).first()
        if invitador:
            invitador.Balance += vip.price * 0.10
            invitador.save()

    messages.success(request, "You have successfully purchased the VIP.")
    return redirect('dashboard')


@login_required
def claim_reward(request, vip_id):
    vip = get_object_or_404(Vips, id=vip_id)
    user = request.user

    # Verificar si el usuario ha comprado el VIP
    purchase = Purchase.objects.filter(user=user, vip=vip).first()
    if not purchase:
        messages.error(request, "You have not purchased this VIP.")
        return redirect('dashboard')

    # Contar la cantidad de veces que se ha reclamado la recompensa
    if not hasattr(purchase, 'reward_count'):
        purchase.reward_count = 0

    # Verificar si la recompensa se ha reclamado 30 veces
    if purchase.reward_count >= 30:
        purchase.delete()
        messages.error(request, "You have used all your daily rewards for this VIP.")
        return redirect('dashboard')

    # Verificar el tiempo desde la última recompensa
    if purchase.last_claimed and (timezone.now() - purchase.last_claimed) < timedelta(hours=24):
        time_remaining = timedelta(hours=24) - (timezone.now() - purchase.last_claimed)
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        messages.error(request, f"You cannot claim another daily reward yet. Try again on {hours} hours & {minutes} minutes.")
        return redirect('dashboard')

    # Añadir la recompensa diaria al balance del usuario
    user.Balance += vip.dreward
    user.save()

    # Actualizar la compra
    purchase.reward_count += 1
    purchase.last_claimed = timezone.now()
    purchase.save()

    messages.success(request, "You have successfully claimed your daily reward.")
    return redirect('dashboard')


@login_required
def create_help_request(request):
    if request.method == 'POST':
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            help_request = form.save(commit=False)
            help_request.user = request.user
            help_request.save()
            messages.success(request, 'Your help request has been submitted.')
            return redirect('dashboard')
        else:
            messages.error(request, 'There was an error with your submission.')

    return redirect('dashboard')


def log_out(request):
    logout(request)
    return redirect('home')
