from django.db import migrations, models
import django.db.models.deletion
import ipam.fields
import netbox_cmdb.fields


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_cmdb", "0051_sonicrolemapping"),
    ]

    operations = [
        migrations.CreateModel(
            name="ManagementRoute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "kind",
                    models.CharField(
                        help_text="Static: default route of the management table. Forced: destination steered through it.",
                        max_length=10,
                    ),
                ),
                (
                    "prefix",
                    ipam.fields.IPNetworkField(
                        help_text="Destination prefix, e.g. 0.0.0.0/0 for the default route."
                    ),
                ),
                (
                    "next_hop",
                    netbox_cmdb.fields.CustomIPAddressField(
                        blank=True,
                        help_text="Gateway of a static route, in the subnet of the interface. Empty for a forced route.",
                        null=True,
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "logical_interface",
                    models.ForeignKey(
                        help_text="The management logical interface the route is attached to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s",
                        to="netbox_cmdb.logicalinterface",
                    ),
                ),
            ],
            options={
                "verbose_name": "Management Route",
                "verbose_name_plural": "Management Routes",
                "unique_together": {("logical_interface", "kind", "prefix")},
            },
        ),
    ]
