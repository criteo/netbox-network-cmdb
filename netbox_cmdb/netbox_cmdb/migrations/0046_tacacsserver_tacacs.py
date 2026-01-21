from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0161_cabling_cleanup'),
        ('netbox_cmdb', '0045_syslogserver_syslog'),
    ]

    operations = [
        migrations.CreateModel(
            name='TacacsServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('server_address', models.GenericIPAddressField()),
                ('priority', models.PositiveIntegerField(default=1)),
                ('tcp_port', models.PositiveIntegerField(default=49)),
            ],
            options={
                'verbose_name_plural': 'Tacacs Servers',
            },
        ),
        migrations.CreateModel(
            name='Tacacs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('passkey', models.CharField(blank=True, max_length=128, null=True)),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dcim.device')),
                ('server_list', models.ManyToManyField(blank=True, default=None, related_name='%(class)s_tacacs_server', to='netbox_cmdb.tacacsserver')),
            ],
            options={
                'verbose_name_plural': 'Tacacs',
            },
        ),
    ]
