from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid


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

    USERNAME_FIELD = "email"
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
