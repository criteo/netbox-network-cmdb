from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0161_cabling_cleanup'),
        ('netbox_cmdb', '0035_vlan'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceInterface',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('enabled', models.BooleanField(default=True)),
                ('state', models.CharField(default='staging', max_length=50)),
                ('monitoring_state', models.CharField(default='disabled', max_length=50)),
                ('autonegotiation', models.BooleanField(default=True)),
                ('speed', models.PositiveIntegerField(blank=True, null=True)),
                ('fec', models.CharField(blank=True, max_length=5, null=True)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)sdevice', to='dcim.device')),
            ],
            options={
                'unique_together': {('device', 'name')},
            },
        ),
    ]
