from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.models import IPAddress

from netbox_cmdb.models import DeviceInterface, LogicalInterface


def create_management_interface(device_name="router-test", address="192.0.2.10/24"):
    """Create a device with a `mgmt0.0` logical interface holding `address`.

    The site, manufacturer, device type and role are reused when they already exist so the
    helper can be called several times in a test.
    """
    site, _ = Site.objects.get_or_create(name="SiteTest", slug="site-test")
    manufacturer, _ = Manufacturer.objects.get_or_create(name="test", slug="test")
    device_type, _ = DeviceType.objects.get_or_create(
        manufacturer=manufacturer, model="model-test", slug="model-test"
    )
    device_role, _ = DeviceRole.objects.get_or_create(name="role-test", slug="role-test")
    device = Device.objects.create(
        name=device_name, device_role=device_role, device_type=device_type, site=site
    )
    device_interface = DeviceInterface.objects.create(name="mgmt0", device=device)
    ipv4_address = IPAddress.objects.create(address=address) if address else None
    return LogicalInterface.objects.create(
        index=0, parent_interface=device_interface, type="l3", ipv4_address=ipv4_address
    )
