# Generated by Django 4.0.1 on 2022-02-13 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cus_manage_app', '0006_customer_user_alter_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='profile_img',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
