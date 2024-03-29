# Generated by Django 4.2.7 on 2024-01-22 10:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("OmniApp", "0026_order_orderitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("shipped", "Shipped"),
                    ("delivered", "Delivered"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
