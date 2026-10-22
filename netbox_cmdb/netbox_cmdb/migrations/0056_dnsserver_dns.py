from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_cmdb", "0055_dhcpserver_dhcprelayinterface"),
    ]

    operations = [
        migrations.CreateModel(
            name="DNSServer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("name", models.CharField(blank=True, default="", max_length=100)),
                ("server_address", models.GenericIPAddressField(unique=True)),
            ],
            options={
                "verbose_name": "DNS Server",
                "verbose_name_plural": "DNS Servers",
            },
        ),
        migrations.CreateModel(
            name="DNS",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "device",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="dcim.device"
                    ),
                ),
                (
                    "server_list",
                    models.ManyToManyField(
                        blank=True,
                        default=None,
                        related_name="%(class)s_dns_server",
                        to="netbox_cmdb.dnsserver",
                    ),
                ),
            ],
            options={
                "verbose_name": "DNS",
                "verbose_name_plural": "DNS",
            },
        ),
    ]
