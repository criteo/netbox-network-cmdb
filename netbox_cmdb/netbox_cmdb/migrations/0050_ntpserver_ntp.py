from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0049_logicalinterface_use_ipv6_link_local_only'),
    ]

    operations = [
        migrations.CreateModel(
            name='NTPServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, default='', max_length=100)),
                ('server_address', models.GenericIPAddressField(unique=True)),
            ],
            options={
                'verbose_name': 'NTP Server',
                'verbose_name_plural': 'NTP Servers',
            },
        ),
        migrations.CreateModel(
            name='NTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dcim.device')),
                ('server_list', models.ManyToManyField(blank=True, default=None, related_name='%(class)s_ntp_server', to='netbox_cmdb.ntpserver')),
            ],
            options={
                'verbose_name': 'NTP',
                'verbose_name_plural': 'NTP',
            },
        ),
    ]
