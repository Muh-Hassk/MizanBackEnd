# Generated by Django 4.2.5 on 2023-10-08 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_rename_userid_conversations_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='content',
            field=models.TextField(),
        ),
    ]