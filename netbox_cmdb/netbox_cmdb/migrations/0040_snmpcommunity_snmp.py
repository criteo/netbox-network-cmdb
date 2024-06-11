from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0161_cabling_cleanup'),
        ('netbox_cmdb', '0039_logicalinterface'),
    ]

    operations = [
        migrations.CreateModel(
            name='SNMPCommunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('community', models.CharField(max_length=31)),
                ('type', models.CharField(default='readonly', max_length=10)),
            ],
            options={
                'verbose_name_plural': 'SNMP Communities',
            },
        ),
        migrations.CreateModel(
            name='SNMP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('location', models.CharField(max_length=31)),
                ('contact', models.CharField(max_length=31)),
                ('community_list', models.ManyToManyField(blank=True, default=None, related_name='%(class)s_community', to='netbox_cmdb.snmpcommunity')),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dcim.device')),
            ],
            options={
                'verbose_name_plural': 'SNMP',
            },
        ),
    ]
