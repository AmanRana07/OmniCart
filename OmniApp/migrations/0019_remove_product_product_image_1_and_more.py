# Generated by Django 4.2.7 on 2024-01-06 05:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("OmniApp", "0018_product_product_image_1_product_product_image_2_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="product_image_1",
        ),
        migrations.RemoveField(
            model_name="product",
            name="product_image_2",
        ),
        migrations.RemoveField(
            model_name="product",
            name="product_image_3",
        ),
    ]