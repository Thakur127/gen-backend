# Generated by Django 4.2.2 on 2023-08-21 08:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0016_course_rating_course_totalratings'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='user',
            new_name='owner',
        ),
    ]
