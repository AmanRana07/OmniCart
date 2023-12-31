# Generated by Django 4.2.7 on 2023-12-28 13:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("OmniApp", "0016_customer_login_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "product_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("product_name", models.CharField(max_length=255)),
                ("quantity", models.PositiveIntegerField()),
                (
                    "product_image",
                    models.ImageField(
                        blank=True, null=True, upload_to="product_images/"
                    ),
                ),
                ("unit_weight", models.FloatField()),
                ("product_description", models.TextField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "manufacturer_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="OmniApp.customer",
                    ),
                ),
            ],
        ),
    ]
