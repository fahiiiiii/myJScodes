# Generated by Django 4.0.10 on 2024-12-02 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_location_center'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodation',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
