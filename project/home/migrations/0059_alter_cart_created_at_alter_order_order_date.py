# Generated by Django 4.2.3 on 2023-09-25 06:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0058_alter_cart_created_at_alter_order_order_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cart",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 25, 12, 25, 5, 68728)
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="order_date",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 25, 12, 25, 5, 68728)
            ),
        ),
    ]
