# Generated by Django 4.2.5 on 2023-09-20 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='accountType',
            field=models.CharField(default='Lawyer', max_length=20),
            preserve_default=False,
        ),
    ]
