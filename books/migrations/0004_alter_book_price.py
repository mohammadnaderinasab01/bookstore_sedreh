# Generated by Django 5.1.1 on 2024-10-07 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_book_price_alter_book_book_file_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='price',
            field=models.IntegerField(),
        ),
    ]
