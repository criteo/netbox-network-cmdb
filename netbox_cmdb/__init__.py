"""Netbox CMDB plugin."""
from extras.plugins import PluginConfig



class CMDB(PluginConfig):
    name = "netbox_cmdb"
    verbose_name = "Netbox CMDB"
    description = "Manages additional fields for CMDB"
    version = "0.1"
    author = "Criteo"
    author_email = "network-team@criteo.com"
    base_url = "cmdb"
    required_settings = []
    default_settings = {}

    def ready(self):
        import netbox_cmdb.signals


config = CMDB
