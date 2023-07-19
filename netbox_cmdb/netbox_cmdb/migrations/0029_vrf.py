from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0007_contact_link'),
        ('netbox_cmdb', '0028_remove_prefixlistterm_decision'),
    ]

    operations = [
        migrations.CreateModel(
            name='VRF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='_vrfs', to='tenancy.tenant')),
            ],
            options={
                'verbose_name': 'VRF',
                'verbose_name_plural': 'VRFs',
                'ordering': ['name'],
            },
        ),
    ]
