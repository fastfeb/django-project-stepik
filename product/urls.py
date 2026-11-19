from django.urls import path
from . import views

app_name = 'product'


urlpatterns = [
    path('', views.home, name='home'),
    path('product/cart_detail/', views.CartDetailView.as_view(), name="cart_detail"),
    path('product/bank_account/', views.bank_account_view, name="bank_account_view"),
    path('product/deposit_account/', views.deposit_account_view, name='deposit_account_view'),
    path("add_deposit/", views.deposit_money_view, name="add_deposit"),
    path('transfer_money/', views.transfer_money_view, name='transfer_money'),
    
]
