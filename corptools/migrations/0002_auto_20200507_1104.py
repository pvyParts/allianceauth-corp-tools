# Generated by Django 2.2.9 on 2020-05-07 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corptools', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mapregion',
            name='description',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
