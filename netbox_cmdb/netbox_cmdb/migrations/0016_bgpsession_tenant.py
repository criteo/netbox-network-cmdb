# Generated by Django 4.0.7 on 2022-08-23 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0007_contact_link'),
        ('netbox_cmdb', '0015_rename_local_asn_and_add_remote_asn'),
    ]

    operations = [
        migrations.AddField(
            model_name='bgpsession',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tenancy.tenant'),
        ),
    ]
