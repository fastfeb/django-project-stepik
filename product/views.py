from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Category, Product, Cart, CartItem, BankAccount, User
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db import transaction
from django.contrib import messages
from decimal import Decimal, InvalidOperation

class HomeView(TemplateView):
    template_name = "templates/product/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["catigories"] = Category.objects.filter(is_active=True)

        category_slug = self.request.GET.get("category")
        if category_slug:
            context['selected_category'] = Category.objects.filter(category_slug, is_active=True).first()
            if context['selected_category']:
                context['product'] = Product.objects.filter(category = context['selected_category'], is_active=True)
            else:
                context['product'] = []
        else:
            context['product'] = []
            context['selected_category'] = None

        return context


@require_POST
@login_required
def add_to_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.update_or_create(cart=cart, product=product, defaults={"quantity":1})

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    referrer_url = request.META.get("HTTP_REFERER")

    if referrer_url:
        return redirect(referrer_url)

    return redirect('product:home')

class CartDetailView(TemplateView):
    template_name = 'product/cart_detail.html'
    model = CartItem
    context_object_name = 'cart_items'

    def get_queryset(self, request):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.request.user.cart
        return context

class CartPurchaseView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user

        try:
            cart = user.cart 
            bank_account = user.bank_account
        except:
            messages.error(request, "У вас нет аккаунта или активной корзины")
            return redirect('homepage:cart_detail')

        total_price = cart.total_price

        if total_price > bank_account.balance:
            messages.error(request, "У вас недостаточно денег для оплаты всей корзины")
            return redirect('homepage:cart_detail')

        with transaction.atomic():
            bank_account.balance -= total_price
            bank_account.save()
            cart.items.all().delete()
        messages.success(request, "Покупка успешна.")
        return redirect('homepage:home')

@login_required
def bank_account_view(request):
    bank_account = get_object_or_404(BankAccount, user=request.user)
    return render(request, 'product/bank_account.html', {'bank_account': bank_account})

@login_required
def deposit_account_view(request):
    bank_account = get_object_or_404(BankAccount, user=request.user)
    return render(request, 'product/deposit_account.html', {'bank_account': bank_account})

@login_required
def deposit_money_view(request):
    bank_account = get_object_or_404(user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError):
            messages.error(request, "Введите корректную сумму больше нуля.")
            return redirect("deposit_account")
        
        bank_account.balance += amount
        bank_account.save()
        return redirect('bank_account')

    return render(request, 'product/deposit_account.html', {'bank_account': bank_account})


@login_required
def transfer_money_view(request):
    sender_account = get_object_or_404(BankAccount, user=request.user)

    if request.method == 'POST':
        recipient_username = request.POST.get('recipient_username')
        recipient_account_number = request.POST.get('recipient_account')
        amount = request.POST.get('amount')
        if not amount:
            messages.error(request, 'Укажите сумму перевода!')
            return redirect("homepage:transfer_money")
        try:
            amount = Decimal(amount)
        except:
            messages.error('Сумма перевода не корректна')
            return redirect("homepage:transfer_money")
        if amount < 0:
            messages.error('Сумма перевода не должна быть меньше 0. Укажите корректную сумму.')
            return redirect('homepage:transfer_money')
        recipient_username = None
        if recipient_username:
          try:
            user = User.objects.get(username=recipient_username)
            recipient_account = BankAccount.objects.get(user=user)
          except User.DoesNotExist:
            messages.error(request, "Пользователь с таким username не найден.")
            return redirect("homepage:transfer_money")
          except BankAccount.DoesNotExist:
            messages.error(request, "У этого пользователя нет банковского счёта.")
            return redirect("homepage:transfer_money")
        elif recipient_account_number:
            try:
                recipient_account = BankAccount.objects.get(account_number=recipient_account_number)
            except User.DoesNotExist:
                messages.error('Пользователь с данным номером аккаунта не существует')
                return redirect('homepage:transfer_money')
            else:
                messages.error('Укажите получателя(номер аккаунта или имя аккаунта)')
                return redirect('homepage:transfer_money')

        if sender_account.balance < amount:
            messages.error('Недостаточно средств на счёте.')
            return redirect('homepage:transfer_money')

        sender_account.balance -= amount
        recipient_account.balance += amount
        sender_account.save()
        recipient_account.save()

        messages.success(request, f'Перевод прошёл успешно. Вы перевели {amount} рублей пользователю {recipient_account.user.username}')
        return redirect('homepage:bank_account')
    return redirect(request, 'homepage:transfer_money.html', {'sender_account': sender_account})





        










