from django.db import migrations, models
import django.db.models.deletion
import ipam.fields


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0043_devicebgpsession_delay_open_timer'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalAfiSafi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('afi_safi_name', models.CharField(max_length=50)),
                ('bgp_global', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='afi_safis', to='netbox_cmdb.bgpglobal')),
            ],
            options={
                'unique_together': {('bgp_global', 'afi_safi_name')},
            },
        ),
        migrations.CreateModel(
            name='RedistributedNetwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('prefix', ipam.fields.IPNetworkField()),
                ('global_afi_safi', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='redistributed_networks', to='netbox_cmdb.globalafisafi')),
            ],
            options={
                'unique_together': {('global_afi_safi', 'prefix')},
            },
        ),
        migrations.CreateModel(
            name='Aggregate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('prefix', ipam.fields.IPNetworkField()),
                ('global_afi_safi', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aggregates', to='netbox_cmdb.globalafisafi')),
            ],
            options={
                'unique_together': {('global_afi_safi', 'prefix')},
            },
        ),
    ]
