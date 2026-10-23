from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_cmdb", "0056_dnsserver_dns"),
    ]

    operations = [
        migrations.AddField(
            model_name="portlayout",
            name="index",
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text="The front-panel port index in the NOS (e.g. 0 for etp0). "
                "Breakout ports share the index of their parent port.",
                null=True,
            ),
        ),
    ]
