import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_cmdb', '0040_snmpcommunity_snmp'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicebgpsession',
            name='delay_open_timer',
            field=models.PositiveSmallIntegerField(blank=True, default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(240)]),
        ),
    ]
