# Generated by Django 4.0.10 on 2024-12-02 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_alter_accommodation_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodation',
            name='id',
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
    ]
