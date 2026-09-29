from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_cmdb", "0048_portlayout_lanes"),
    ]

    operations = [
        migrations.AddField(
            model_name="logicalinterface",
            name="use_ipv6_link_local_only",
            field=models.BooleanField(default=False),
        ),
    ]
