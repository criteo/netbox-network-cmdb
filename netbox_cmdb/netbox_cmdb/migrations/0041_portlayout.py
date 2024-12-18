from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0161_cabling_cleanup'),
        ('netbox_cmdb', '0040_snmpcommunity_snmp'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortLayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=64)),
                ('label_name', models.CharField(max_length=64)),
                ('logical_name', models.CharField(max_length=64)),
                ('vendor_name', models.CharField(max_length=64)),
                ('vendor_short_name', models.CharField(max_length=64)),
                ('vendor_long_name', models.CharField(max_length=64)),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_device_type', to='dcim.devicetype')),
                ('network_role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_network_role', to='dcim.devicerole')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
