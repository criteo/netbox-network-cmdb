from django.core.exceptions import ValidationError
from ipam.fields import IPAddressField
from ipam.formfields import IPAddressFormField
from netaddr import AddrFormatError, IPAddress


class CustomIPAddressField(IPAddressField):
    """
    IP address
    """

    def python_type(self):
        return IPAddress

    def form_class(self):
        return IPAddressFormField

    def to_python(self, value):
        if not value:
            return value
        try:
            return IPAddress(value)
        except AddrFormatError:
            raise ValidationError("Invalid IP address format: {}".format(value))
        except (TypeError, ValueError) as e:
            raise ValidationError(e)
