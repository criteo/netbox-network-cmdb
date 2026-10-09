from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0052_managementroute'),
    ]

    operations = [
        migrations.CreateModel(
            name='SonicHwskuMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('hwsku', models.CharField(max_length=255)),
                ('device_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sonic_hwsku_mapping', to='dcim.devicetype')),
            ],
            options={
                'verbose_name': 'SONiC HwSKU Mapping',
                'verbose_name_plural': 'SONiC HwSKU Mappings',
                'ordering': ['device_type__model'],
            },
        ),
    ]
