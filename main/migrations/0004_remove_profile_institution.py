# Generated by Django 4.2 on 2023-04-10 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_profile_institution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='institution',
        ),
    ]
