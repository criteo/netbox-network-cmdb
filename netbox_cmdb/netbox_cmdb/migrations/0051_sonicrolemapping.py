from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0050_ntpserver_ntp'),
    ]

    operations = [
        migrations.CreateModel(
            name='SonicRoleMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('sonic_type', models.CharField(choices=[('ToRRouter', 'ToRRouter'), ('LeafRouter', 'LeafRouter'), ('SpineRouter', 'SpineRouter'), ('not-provisioned', 'not-provisioned')], default='not-provisioned', max_length=50)),
                ('device_role', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sonic_role_mapping', to='dcim.devicerole')),
            ],
            options={
                'verbose_name': 'SONiC Role Mapping',
                'verbose_name_plural': 'SONiC Role Mappings',
                'ordering': ['device_role__name'],
            },
        ),
    ]
