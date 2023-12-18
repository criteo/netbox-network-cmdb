from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0007_contact_link'),
        ('netbox_cmdb', '0037_alter_vlan_unique_together_remove_vlan_device'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vrf',
            unique_together={('tenant', 'name')},
        ),
        migrations.RemoveField(
            model_name='vrf',
            name='device',
        ),
    ]
