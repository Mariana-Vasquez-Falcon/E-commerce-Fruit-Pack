# Generated by Django 5.1.1 on 2024-11-02 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pp2', '0007_auto_20241026_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='img/productos/'),
        ),
    ]
