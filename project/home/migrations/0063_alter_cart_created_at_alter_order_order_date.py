# Generated by Django 4.2.3 on 2023-09-25 11:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0062_alter_cart_created_at_alter_order_order_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cart",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 25, 16, 43, 29, 689055)
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="order_date",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 25, 16, 43, 29, 689055)
            ),
        ),
    ]
