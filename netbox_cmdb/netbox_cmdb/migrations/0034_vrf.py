from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0007_contact_link'),
        ('dcim', '0161_cabling_cleanup'),
        ('netbox_cmdb', '0033_delete_vrf'),
    ]

    operations = [
        migrations.CreateModel(
            name='VRF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)sdevice', to='dcim.device')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)stenant', to='tenancy.tenant')),
            ],
            options={
                'verbose_name': 'VRF',
                'verbose_name_plural': 'VRFs',
                'ordering': ['name'],
                'unique_together': {('device', 'name')},
            },
        ),
    ]
