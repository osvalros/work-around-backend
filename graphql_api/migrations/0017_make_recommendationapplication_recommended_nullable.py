# Generated by Django 3.2.8 on 2021-10-17 04:31

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graphql_api', '0016_add_recommendations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendationapplication',
            name='recommended',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='graphql_api.recommendationapplication'),
        ),
    ]
