# Generated by Django 4.2.3 on 2023-08-08 10:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("adm", "0018_remove_admproducts_colors_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariant",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="variant_images/"),
        ),
    ]
