# Generated by Django 4.2.2 on 2023-07-07 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='image_url',
            field=models.URLField(blank=True),
        ),
    ]
