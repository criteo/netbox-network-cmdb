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
    PluginMenuItem(
        link="plugins:netbox_cmdb:routepolicy_list",
        link_text="Route Policies",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:routepolicy_add",
                title="Route Policies",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_cmdb:snmp_list",
        link_text="SNMP",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:snmp_add",
                title="SNMP",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_cmdb:snmpcommunity_list",
        link_text="SNMP Community",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:snmpcommunity_add",
                title="SNMP Community",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_cmdb:syslog_list",
        link_text="Syslog",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:syslog_add",
                title="Syslog",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_cmdb:syslogserver_list",
        link_text="Syslog Server",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:syslogserver_add",
                title="Syslog Server",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_cmdb:tacacs_list",
        link_text="Tacacs",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:tacacs_add",
                title="Tacacs",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_cmdb:tacacsserver_list",
        link_text="Tacacs Server",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_cmdb:tacacsserver_add",
                title="Tacacs Server",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
)
