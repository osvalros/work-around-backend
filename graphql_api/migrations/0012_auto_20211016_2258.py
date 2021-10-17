# Generated by Django 3.2.8 on 2021-10-16 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graphql_api', '0011_add_facility_type_to_application'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commutetype',
            name='name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='facilitytype',
            name='name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lifestyletype',
            name='name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='propertytype',
            name='name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
