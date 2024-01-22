from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from django.contrib.auth.models import User


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class Customer(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ("user", "User"),
        ("manufacturer", "Manufacturer"),
    ]

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    login_status = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["username"]

    # def __str__(self):
    #     return str(self.id)

    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return None

    @staticmethod
    def get_customer_by_username(username):
        try:
            return Customer.objects.get(username=username)
        except Customer.DoesNotExist:
            return None


class Product(models.Model):
    product_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    product_name = models.CharField(max_length=255)
    manufacturer_id = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="products"
    )
    quantity = models.PositiveIntegerField()
    product_image = models.ImageField(
        upload_to="product_images/", null=True, blank=True
    )
    unit_weight = models.FloatField()
    product_description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_short_description = models.TextField(default=" ")

    def __str__(self):
        return self.product_name


# Add to Cart Functionality


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="23223")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        # Update the cart's total price and total quantity when saving a CartItem
        self.cart.total_price += self.product.unit_price * self.quantity
        self.cart.total_quantity += self.quantity
        self.cart.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Update the cart's total price and total quantity when deleting a CartItem
        self.cart.total_price -= self.product.unit_price * self.quantity
        self.cart.total_quantity -= self.quantity
        self.cart.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} in {self.cart.user.username}'s Cart"
