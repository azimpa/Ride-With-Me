# Generated by Django 4.2.3 on 2023-09-22 11:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("adm", "0036_remove_coupon_active_coupon_is_expired_usercoupons"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coupon",
            name="is_expired",
            field=models.BooleanField(default=True),
        ),
    ]
