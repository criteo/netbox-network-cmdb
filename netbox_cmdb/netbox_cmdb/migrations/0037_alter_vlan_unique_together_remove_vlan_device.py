from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0036_deviceinterface'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vlan',
            unique_together={('vid', 'name')},
        ),
        migrations.RemoveField(
            model_name='vlan',
            name='device',
        ),
    ]
