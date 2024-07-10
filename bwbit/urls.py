"""
URL configuration for bwbit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from webapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login_users/', login_users, name='login_users'),
    path('register/', register, name='register'),
    path('update_wallet/', update_wallet, name='update_wallet'),
    path('request_balance/', request_balance, name='request_balance'),
    path('request_balance/', request_balance, name='request_balance'),
    path('approve_balance_request/<int:request_id>/', approve_balance_request, name='approve_balance_request'),
    path('delete_balance_request/<int:request_id>/', delete_balance_request, name='delete_balance_request'),
    path('request_withdrawal/', request_withdrawal, name='request_withdrawal'),
    path('approve_withdrawal/<int:req_id>/', approve_withdrawal, name='approve_withdrawal'),
    path('dashboard/', dashboard, name='dashboard'),
    path('comprar_vip/<int:vip_id>/', comprar_vip, name='comprar_vip'),
    path('claim_reward/<int:vip_id>/', claim_reward, name='claim_reward'),
    path('create_help_request/', create_help_request, name='create_help_request'),
    path('log_out/', log_out, name='log_out'),
]
