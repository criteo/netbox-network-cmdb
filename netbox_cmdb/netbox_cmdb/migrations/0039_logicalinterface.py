from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0060_alter_l2vpn_slug'),
        ('netbox_cmdb', '0038_alter_vrf_unique_together_remove_vrf_device'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogicalInterface',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('index', models.PositiveSmallIntegerField()),
                ('enabled', models.BooleanField(default=True)),
                ('state', models.CharField(default='staging', max_length=50)),
                ('monitoring_state', models.CharField(default='disabled', max_length=50)),
                ('mtu', models.PositiveIntegerField(blank=True, null=True)),
                ('type', models.CharField(default=None, max_length=2)),
                ('mode', models.CharField(blank=True, default=None, max_length=20, null=True)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('ipv4_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_ipv4_address', to='ipam.ipaddress')),
                ('ipv6_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_ipv6_address', to='ipam.ipaddress')),
                ('native_vlan', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_native_vlan', to='netbox_cmdb.vlan')),
                ('parent_interface', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='netbox_cmdb.deviceinterface')),
                ('tagged_vlans', models.ManyToManyField(blank=True, default=None, related_name='%(class)s_tagged_vlans', to='netbox_cmdb.vlan')),
                ('untagged_vlan', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_untagged_vlan', to='netbox_cmdb.vlan')),
                ('vrf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_vrf', to='netbox_cmdb.vrf')),
            ],
            options={
                'unique_together': {('index', 'parent_interface')},
            },
        ),
    ]
