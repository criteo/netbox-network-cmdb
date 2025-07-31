from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0041_portlayout'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('state', models.CharField(default='staging', max_length=50)),
                ('monitoring_state', models.CharField(default='disabled', max_length=50)),
                ('interface_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_interface_a', to='netbox_cmdb.deviceinterface')),
                ('interface_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_interface_b', to='netbox_cmdb.deviceinterface')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
