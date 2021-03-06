# Generated by Django 3.2.8 on 2021-10-17 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graphql_api', '0015_alter_application_preferred_cities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='length_of_stay',
            field=models.IntegerField(choices=[(3, 'Three Months'), (6, 'Six Months'), (12, 'Twelve Months'), (24, 'Twenty Four Months')], default=3),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application',
            name='property',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='graphql_api.property'),
            preserve_default=False,
        ),
    ]
