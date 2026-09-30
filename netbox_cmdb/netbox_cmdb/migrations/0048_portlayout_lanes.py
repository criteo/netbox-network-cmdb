import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_cmdb", "0047_syslogserver_server_address_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="portlayout",
            name="lanes",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(),
                blank=True,
                default=list,
                help_text="The ASIC lanes used by the interface, in hardware order (e.g. 0,1,2,3).",
                size=None,
            ),
        ),
    ]
