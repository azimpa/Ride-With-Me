# Generated by Django 4.2.3 on 2023-09-28 13:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0064_order_coupon_discount_alter_cart_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="cart_total",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="cart",
            name="total_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name="cart",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 28, 18, 49, 42, 92247)
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="order_date",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 28, 18, 49, 42, 92247)
            ),
        ),
    ]
