# Generated by Django 4.0.8 on 2023-04-06 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0026_alter_devicebgpsession_local_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bgpcommunitylistterm',
            name='decision',
        ),
    ]
