# Generated by Django 4.0.10 on 2024-12-03 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_alter_accommodation_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodation',
            name='amenities',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
