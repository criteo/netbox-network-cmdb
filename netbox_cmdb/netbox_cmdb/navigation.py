"""Navigation (menu)."""

from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_cmdb:asn_list",
        link_text="AS Numbers",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:asn_add",
                title="AS Numbers",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_cmdb:bgpsession_list",
        link_text="BGP Sessions",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:bgpsession_add",
                title="BGP Sessions",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_cmdb:bgppeergroup_list",
        link_text="BGP Peer Groups",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:bgppeergroup_add",
                title="BGP Peer Groups",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
)
