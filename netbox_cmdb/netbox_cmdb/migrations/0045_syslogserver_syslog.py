from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0161_cabling_cleanup'),
        ('netbox_cmdb', '0044_globalafisafi_redistributednetwork_aggregate'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyslogServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('server_address', models.GenericIPAddressField()),
            ],
            options={
                'verbose_name_plural': 'Syslog Servers',
            },
        ),
        migrations.CreateModel(
            name='Syslog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dcim.device')),
                ('server_list', models.ManyToManyField(blank=True, default=None, related_name='%(class)s_syslog_server', to='netbox_cmdb.syslogserver')),
            ],
            options={
                'verbose_name_plural': 'Syslog',
            },
        ),
    ]
