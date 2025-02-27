# Generated by Django 5.1.4 on 2025-01-27 21:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride_system', '0005_remove_driver_username_driver_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination', models.CharField(max_length=200)),
                ('date', models.DateTimeField()),
                ('time', models.TimeField()),
                ('number', models.IntegerField()),
                ('car_type', models.CharField(max_length=200)),
                ('special', models.CharField(max_length=200)),
                ('isShared', models.BooleanField()),
                ('isConfirmed', models.BooleanField(default=False)),
                ('isComplete', models.BooleanField(default=False)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ride_system.driver')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_trips', to='ride_system.account')),
                ('shareSet', models.ManyToManyField(to='ride_system.account')),
            ],
        ),
    ]
