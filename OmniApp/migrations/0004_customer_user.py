# Generated by Django 4.2.7 on 2023-12-25 15:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("OmniApp", "0003_customer_otp_email_customer_otp_email_verified_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="user",
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
