# Generated by Django 5.1.1 on 2024-10-07 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='price',
            field=models.IntegerField(default=0, max_length=7),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='book',
            name='book_file_url',
            field=models.TextField(default=0, max_length=1000),
            preserve_default=False,
        ),
    ]
