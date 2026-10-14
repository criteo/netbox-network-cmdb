from netbox_cmdb.models import DeviceInterface, LogicalInterface
from netbox_cmdb.tests.management_route.common import create_management_interface


def create_logical_interface(device_name="router-test", port="Ethernet10", type="l3"):
    """Create a device with a `<port>.0` logical interface of the given type."""
    mgmt = create_management_interface(device_name=device_name, address=None)
    device_interface = DeviceInterface.objects.create(
        name=port, device=mgmt.parent_interface.device
    )
    return LogicalInterface.objects.create(index=0, parent_interface=device_interface, type=type)
