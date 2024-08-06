# Generated by Django 4.2.3 on 2023-08-01 18:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("adm", "0004_rename_admcatogories_admcategories"),
    ]

    operations = [
        migrations.AlterField(
            model_name="admproducts",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="adm.admcategories",
            ),
        ),
    ]
