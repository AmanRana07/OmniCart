# Generated by Django 4.2.7 on 2023-12-27 13:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("OmniApp", "0015_remove_customer_otp_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="login_status",
            field=models.BooleanField(default=False),
        ),
    ]
