# Generated by Django 5.1.1 on 2024-11-02 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pp2', '0008_alter_producto_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='pp2/static/img/productos/'),
        ),
    ]
