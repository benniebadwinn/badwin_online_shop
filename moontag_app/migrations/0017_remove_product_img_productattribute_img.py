# Generated by Django 4.0.6 on 2022-08-10 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moontag_app', '0016_rename_catagory_product_category_alter_banner_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='img',
        ),
        migrations.AddField(
            model_name='productattribute',
            name='img',
            field=models.ImageField(null=True, upload_to='media/product_images'),
        ),
    ]
