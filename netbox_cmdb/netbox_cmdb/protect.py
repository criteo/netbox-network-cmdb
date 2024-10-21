MODELS_LINKED_TO_DEVICE = {}
MODELS_LINKED_TO_IP_ADDRESS = {}


def from_device_name_change(*fields):
    """Protects from Device name changes in NetBox DCIM.

    This is useful only to prevent Device name changes when CMDB is linked to it.
    """

    def decorator(cls):
        if cls not in MODELS_LINKED_TO_DEVICE:
            MODELS_LINKED_TO_DEVICE[cls] = set()

        if not fields:
            return cls

        for field in fields:
            MODELS_LINKED_TO_DEVICE[cls].add(field)

        return cls

    return decorator


def from_ip_address_change(*fields):
    """Protects from IP Address "address" changes in NetBox IPAM.

    This is useful only to prevent IP Address "address" changes when CMDB is linked to it.
    """

    def decorator(cls):
        if cls not in MODELS_LINKED_TO_IP_ADDRESS:
            MODELS_LINKED_TO_IP_ADDRESS[cls] = set()

        if not fields:
            return cls

        for field in fields:
            MODELS_LINKED_TO_IP_ADDRESS[cls].add(field)

        return cls

    return decorator
