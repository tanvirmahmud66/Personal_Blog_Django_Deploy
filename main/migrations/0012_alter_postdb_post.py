# Generated by Django 4.1.7 on 2023-04-25 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_postcomments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postdb',
            name='post',
            field=models.TextField(blank=True, null=True),
        ),
    ]