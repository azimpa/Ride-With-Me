# Generated by Django 4.2.3 on 2023-10-01 12:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0073_alter_cart_created_at_alter_order_order_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cart",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 10, 1, 18, 11, 18, 937298)
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="order_date",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 10, 1, 18, 11, 18, 937298)
            ),
        ),
    ]
