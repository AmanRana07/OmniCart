# Generated by Django 4.2.7 on 2024-01-06 21:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("OmniApp", "0020_alter_product_product_short_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_short_description",
            field=models.TextField(),
        ),
    ]