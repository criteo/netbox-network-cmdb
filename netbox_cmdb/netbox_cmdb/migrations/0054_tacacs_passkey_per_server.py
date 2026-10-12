from django.db import migrations, models


def copy_device_passkeys_to_servers(apps, schema_editor):
    """Give each TacacsServer the passkey its devices used.

    The passkey moves from the device configuration to the server. A server shared by devices
    with different passkeys cannot get one without guessing: the migration refuses, naming the
    servers, and the passkeys are to be made consistent first. Passkeys are never logged.
    A passkey on a device without any server had no use and is not carried over.
    """
    Tacacs = apps.get_model("netbox_cmdb", "Tacacs")
    TacacsServer = apps.get_model("netbox_cmdb", "TacacsServer")

    conflicting_servers = []
    for server in TacacsServer.objects.all():
        passkeys = set(
            Tacacs.objects.filter(server_list=server)
            .exclude(passkey__isnull=True)
            .exclude(passkey="")
            .values_list("passkey", flat=True)
        )
        if len(passkeys) > 1:
            conflicting_servers.append(server.server_address)
        elif passkeys:
            server.passkey = passkeys.pop()
            server.save()

    if conflicting_servers:
        raise RuntimeError(
            "The devices of these TACACS servers use different passkeys, make them consistent "
            f"before migrating: {', '.join(sorted(conflicting_servers))}"
        )


def copy_server_passkeys_to_devices(apps, schema_editor):
    """Give each Tacacs configuration back the passkey of its servers, when they agree."""
    Tacacs = apps.get_model("netbox_cmdb", "Tacacs")

    for tacacs in Tacacs.objects.all():
        passkeys = {server.passkey for server in tacacs.server_list.all() if server.passkey}
        if len(passkeys) == 1:
            tacacs.passkey = passkeys.pop()
            tacacs.save()


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_cmdb", "0053_sonichwskumapping"),
    ]

    operations = [
        migrations.AddField(
            model_name="tacacsserver",
            name="passkey",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.RunPython(copy_device_passkeys_to_servers, copy_server_passkeys_to_devices),
        migrations.RemoveField(
            model_name="tacacs",
            name="passkey",
        ),
    ]
