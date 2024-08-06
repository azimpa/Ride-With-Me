# Generated by Django 4.2.3 on 2023-09-06 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("adm", "0029_admproducts_is_active_productvariant_is_active_and_more"),
        ("home", "0025_remove_order_order_status_orderitem_order_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cartitem",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="adm.productvariant"
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="adm.productvariant"
            ),
        ),
    ]
