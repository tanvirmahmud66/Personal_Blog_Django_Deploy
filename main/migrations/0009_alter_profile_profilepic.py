# Generated by Django 4.1.7 on 2023-04-14 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_profile_profilepic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profilePic',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
