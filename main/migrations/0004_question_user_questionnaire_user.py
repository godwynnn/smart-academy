# Generated by Django 5.1.3 on 2025-07-14 23:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_otp_profile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_questions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_questionaires', to=settings.AUTH_USER_MODEL),
        ),
    ]
