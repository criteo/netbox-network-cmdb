from dcim.models import Device
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from ipam.models import IPAddress

from netbox_cmdb import protect
from netbox_cmdb.models.bgp import BGPSession


@receiver(post_delete, sender=BGPSession)
def clean_device_bgp_sessions(sender, instance, **kwargs):
    if instance.peer_a:
        a = instance.peer_a
        a.delete()

    if instance.peer_b:
        b = instance.peer_b
        b.delete()


@receiver(pre_save, sender=Device)
def protect_from_device_name_change(sender, instance, **kwargs):
    """Prevents any name changes for dcim.Device if there is a CMDB object linked to it.

    Some models in the CMDB depends on NetBox Device native model.
    If one changes the Device name, it might affect the CMDB as a side effect, and could cause
    unwanted configuration changes.
    """

    if not instance.pk:
        return

    current = Device.objects.get(pk=instance.pk)

    if current.name == instance.name:
        return

    for model, fields in protect.MODELS_LINKED_TO_DEVICE.items():
        if not fields:
            continue

        for field in fields:
            filter = {field: instance}
            if model.objects.filter(**filter).exists():
                raise ValidationError(
                    f"Device name cannot be changed because it is linked to: {model}."
                )


@receiver(pre_save, sender=IPAddress)
def protect_from_ip_address_change(sender, instance, **kwargs):
    """Prevents any name changes for ipam.IPAddress if there is a CMDB object linked to it.

    Some models in the CMDB depends on NetBox IPAddress native model.
    If one changes the address, it might affect the CMDB as a side effect, and could cause
    unwanted configuration changes.
    """
    if not instance.pk:
        return

    current = IPAddress.objects.get(pk=instance.pk)

    if current.address.ip == instance.address.ip:
        return

    for model, fields in protect.MODELS_LINKED_TO_IP_ADDRESS.items():
        if not fields:
            continue

        for field in fields:
            filter = {field: instance}
            if model.objects.filter(**filter).exists():
                raise ValidationError(
                    f"IP address cannot be changed because it is linked to: {model}."
                )
