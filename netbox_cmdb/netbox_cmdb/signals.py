from django.db.models.signals import post_delete
from django.dispatch import receiver
from netbox_cmdb.models.bgp import BGPSession


@receiver(post_delete, sender=BGPSession)
def clean_device_bgp_sessions(sender, instance, **kwargs):
    if instance.peer_a:
        a = instance.peer_a
        a.delete()

    if instance.peer_b:
        b = instance.peer_b
        b.delete()
