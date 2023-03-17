# Generated by Django 4.0.8 on 2022-11-17 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0019_afisafi_device_bgp_session'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='afisafi',
            unique_together={('device_bgp_session', 'afi_safi_name')},
        ),
        migrations.RemoveField(
            model_name='afisafi',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='afisafi',
            name='object_id',
        ),
    ]