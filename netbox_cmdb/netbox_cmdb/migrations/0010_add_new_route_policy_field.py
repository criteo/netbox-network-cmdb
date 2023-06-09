# Generated by Django 3.2.11 on 2022-01-19 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0009_rework_route_pol_and_add_afisafi'),
    ]

    operations = [
        migrations.AddField(
            model_name='afisafi',
            name='route_policy_in',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='afisafi_in', to='netbox_cmdb.routepolicy'),
        ),
        migrations.AddField(
            model_name='afisafi',
            name='route_policy_out',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='afisafi_out', to='netbox_cmdb.routepolicy'),
        ),
        migrations.AddField(
            model_name='bgppeergroup',
            name='route_policy_in',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bgppeergroup_in', to='netbox_cmdb.routepolicy'),
        ),
        migrations.AddField(
            model_name='bgppeergroup',
            name='route_policy_out',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bgppeergroup_out', to='netbox_cmdb.routepolicy'),
        ),
        migrations.AddField(
            model_name='devicebgpsession',
            name='route_policy_in',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='devicebgpsession_in', to='netbox_cmdb.routepolicy'),
        ),
        migrations.AddField(
            model_name='devicebgpsession',
            name='route_policy_out',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='devicebgpsession_out', to='netbox_cmdb.routepolicy'),
        ),
        migrations.AlterField(
            model_name='afisafi',
            name='route_policies_in',
            field=models.ManyToManyField(blank=True, related_name='old_afisafi_in', to='netbox_cmdb.RoutePolicy'),
        ),
        migrations.AlterField(
            model_name='afisafi',
            name='route_policies_out',
            field=models.ManyToManyField(blank=True, related_name='old_afisafi_out', to='netbox_cmdb.RoutePolicy'),
        ),
        migrations.AlterField(
            model_name='bgppeergroup',
            name='route_policies_in',
            field=models.ManyToManyField(blank=True, related_name='old_bgppeergroup_in', to='netbox_cmdb.RoutePolicy'),
        ),
        migrations.AlterField(
            model_name='bgppeergroup',
            name='route_policies_out',
            field=models.ManyToManyField(blank=True, related_name='old_bgppeergroup_out', to='netbox_cmdb.RoutePolicy'),
        ),
        migrations.AlterField(
            model_name='devicebgpsession',
            name='route_policies_in',
            field=models.ManyToManyField(blank=True, related_name='old_devicebgpsession_in', to='netbox_cmdb.RoutePolicy'),
        ),
        migrations.AlterField(
            model_name='devicebgpsession',
            name='route_policies_out',
            field=models.ManyToManyField(blank=True, related_name='old_devicebgpsession_out', to='netbox_cmdb.RoutePolicy'),
        ),
    ]
