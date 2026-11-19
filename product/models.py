from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
import uuid

class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название", unique=True)
    slug = models.SlugField(verbose_name="Слаг", unique=True)
    description = models.TextField(verbose_name= "Описание категории", blank=True)
    image = models.ImageField(verbose_name="Картинка категории", blank=True, upload_to='categories/')
    is_active = models.BooleanField(verbose_name="Активноть категории", default=True)
    created_at = models.DateTimeField(verbose_name="Когда создана категория", default=timezone.now, editable=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлена категория", auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT, verbose_name="Категория")
    name = models.CharField(max_length=150, verbose_name="Название")
    sku = models.CharField(max_length=80, unique=True, verbose_name="Артикул")
    slug = models.SlugField(verbose_name="Слаг", unique=True)
    description_short = models.CharField(max_length=100, verbose_name="Краткое описание")
    description = models.TextField(verbose_name="Полное описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена товара", validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0, verbose_name="Наличие товара на складе")
    image_product = models.ImageField(verbose_name="Картинка товара", blank=True, upload_to='categories/')
    is_active = models.BooleanField(verbose_name="Активноть товара", default=True)
    created_at = models.DateTimeField(verbose_name="Когда создана категория", default=timezone.now, editable=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлена категория", auto_now_add=True)

    class Meta:
            ordering = ("name",)
    
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart", verbose_name="Пользователь")
    created_at = models.DateTimeField("Создано", default=timezone.now, editable=True)
    updated_at = models.DateTimeField("Обновлено", auto_now_add=True)
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="Корзина", related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.ForeignKey(Product, on_delete=models.CASCADE, default=0, verbose_name="Количество")
    unique_together = models.PositiveIntegerField("Уникальность товара", default=1)

    class Meta:
        verbose_name = "Количество товара в корзине"
        verbose_name_plural = "Количество товаров в корзине"
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} {self.quantity} шт."

    @property
    def total_price(self):
        return self.product * self.quantity


class BankAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name="Пользователь")
    account_number = models.CharField(max_length=20, editable=True, unique=True, verbose_name="ID аккаунта")
    balance = models.DecimalField(default=0.00, max_digits=40, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)

    def generate_account_number(self):
        return "2065" + str(uuid.uuid4().int[:12])

    def __str__(self):
        return f"У пользователя {self.user}-{self.account_number} баланс составляет: {self.balance} "






