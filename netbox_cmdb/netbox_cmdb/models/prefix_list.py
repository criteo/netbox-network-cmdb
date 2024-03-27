"""Prefix list models."""

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from ipam.fields import IPNetworkField
from netbox.models import ChangeLoggedModel
from utilities.choices import ChoiceSet


class PrefixListIPVersionChoices(ChoiceSet):
    """Prefix list IP versions choices."""

    IPV4 = "ipv4"
    IPV6 = "ipv6"

    CHOICES = (
        (IPV4, "IPv4"),
        (IPV6, "IPv6"),
    )


class PrefixList(ChangeLoggedModel):
    """Prefix list main model."""

    name = models.CharField(max_length=100)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="%(class)sdevice",
        null=False,
        blank=False,
    )
    ip_version = models.CharField(
        max_length=10,
        choices=PrefixListIPVersionChoices,
        default=PrefixListIPVersionChoices.IPV4,
        help_text="IP version of the prefix list",
    )

    def __str__(self):
        return f"{self.device}-{self.name}"

    class Meta:
        unique_together = ("name", "device")


class PrefixListTerm(ChangeLoggedModel):
    """Prefix list term model."""

    prefix_list = models.ForeignKey(
        to="PrefixList", on_delete=models.CASCADE, related_name="prefix_list_term"
    )
    sequence = models.PositiveIntegerField()
    prefix = IPNetworkField()
    le = models.PositiveSmallIntegerField(null=True, blank=True)
    ge = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return str(f"{self.prefix_list} seq:{self.sequence}")

    @staticmethod
    def _is_mask_len_operator_valid(mask_len, prefix_mask_len, max_prefix_len):
        if mask_len <= prefix_mask_len or mask_len > max_prefix_len:
            return False
        return True

    def clean(self):
        super().clean()

        prefix_mask_len = self.prefix.netmask.netmask_bits()

        if self.prefix_list.ip_version == PrefixListIPVersionChoices.IPV4:
            max_prefix_len = 32
            ip_version = 4
        else:
            max_prefix_len = 128
            ip_version = 6

        # we ensure that the IP prefix matches the version of the parent prefix list.
        if self.prefix.version != ip_version:
            raise ValidationError(
                "Invalid IP prefix, IP version mismatch: IPv{} instead of IPv{}".format(
                    self.prefix.version, ip_version
                )
            )

        # ge can't be lower than the prefix netmask, and greater than the IP version maximum prefix length.
        if self.ge and not self._is_mask_len_operator_valid(
            self.ge, prefix_mask_len, max_prefix_len
        ):
            raise ValidationError("Invalid ge value")

        # le can't be lower than the prefix netmask, and greater than the IP version maximum prefix length.
        if self.le and not self._is_mask_len_operator_valid(
            self.le, prefix_mask_len, max_prefix_len
        ):
            raise ValidationError("Invalid le value")

        # le must be a value lower than ge
        if self.le and self.ge and self.le < self.ge:
            raise ValidationError("Invalid values for le and ge, le should be lower than ge")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("prefix_list", "sequence")
        ordering = ["sequence"]
