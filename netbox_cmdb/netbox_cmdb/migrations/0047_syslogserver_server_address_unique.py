from django.db import migrations, models
from django.db.models import Count


def merge_duplicate_servers(apps, schema_editor):
    """Collapse SyslogServers sharing an address before the unique constraint is added.

    Syslog shipped without the constraint, so a deployed database may already hold
    duplicates: adding unique=True on such a table fails. For each duplicated address the
    oldest row is kept, the configurations referencing the others are repointed to it, and
    the leftovers are deleted. A clean database makes this a no-op.
    """
    SyslogServer = apps.get_model("netbox_cmdb", "SyslogServer")
    Syslog = apps.get_model("netbox_cmdb", "Syslog")

    duplicated_addresses = (
        SyslogServer.objects.values("server_address")
        .annotate(occurrences=Count("id"))
        .filter(occurrences__gt=1)
        .values_list("server_address", flat=True)
    )

    for address in duplicated_addresses:
        servers = list(SyslogServer.objects.filter(server_address=address).order_by("id"))
        kept, duplicates = servers[0], servers[1:]

        for syslog in Syslog.objects.filter(server_list__in=duplicates).distinct():
            syslog.server_list.remove(*duplicates)
            syslog.server_list.add(kept)

        for duplicate in duplicates:
            duplicate.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_cmdb", "0046_tacacsserver_tacacs"),
    ]

    operations = [
        # Merging is not reversible: the duplicates it removed cannot be told apart afterwards.
        migrations.RunPython(merge_duplicate_servers, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="syslogserver",
            name="server_address",
            field=models.GenericIPAddressField(unique=True),
        ),
    ]
