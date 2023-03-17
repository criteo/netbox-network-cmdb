from django.db import models
from netbox.models import ChangeLoggedModel


class Circuit(ChangeLoggedModel):
    """Simple circuits."""

    name = models.CharField(max_length=100, unique=True)
