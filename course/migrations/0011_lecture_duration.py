# Generated by Django 4.2.2 on 2023-08-07 12:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0010_lecture_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]
