# Generated by Django 4.2.7 on 2023-12-25 16:09

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("OmniApp", "0010_alter_customer_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="id",
            field=models.UUIDField(
                auto_created=True,
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
