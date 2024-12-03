# Generated by Django 4.0.10 on 2024-12-03 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_alter_accommodation_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodation',
            name='bedroom_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='accommodation',
            name='images',
            field=models.JSONField(default=list),
        ),
    ]