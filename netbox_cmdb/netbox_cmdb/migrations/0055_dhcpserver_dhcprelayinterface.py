from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_cmdb", "0054_tacacs_passkey_per_server"),
    ]

    operations = [
        migrations.CreateModel(
            name="DhcpServer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("server_address", models.GenericIPAddressField(unique=True)),
            ],
            options={
                "verbose_name_plural": "Dhcp Servers",
            },
        ),
        migrations.CreateModel(
            name="DhcpRelayInterface",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "logical_interface",
                    models.OneToOneField(
                        help_text="The l3 logical interface the DHCP relay is set on.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s",
                        to="netbox_cmdb.logicalinterface",
                    ),
                ),
                (
                    "server_list",
                    models.ManyToManyField(
                        blank=True,
                        default=None,
                        related_name="%(class)s_dhcp_server",
                        to="netbox_cmdb.dhcpserver",
                    ),
                ),
            ],
            options={
                "verbose_name": "Dhcp Relay Interface",
                "verbose_name_plural": "Dhcp Relay Interfaces",
            },
        ),
    ]
