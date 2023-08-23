# Generated by Django 4.2.2 on 2023-07-29 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_alter_review_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.CharField(choices=[('MA', 'Mathematics'), ('PH', 'Physics'), ('EC', 'Economics'), ('FM', 'Finance & Marketing'), ('CS', 'Computer Science'), ('NS', 'Not Specified')], default='NS', max_length=32),
        ),
    ]
