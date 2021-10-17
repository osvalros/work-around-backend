# Generated by Django 3.2.8 on 2021-10-16 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graphql_api', '0004_auto_20211016_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pet_friendly', models.BooleanField(blank=True, null=True)),
                ('move_in_date', models.DateField(blank=True, null=True)),
                ('length_of_stay', models.IntegerField(blank=True, choices=[(3, 'Three Months'), (6, 'Six Months'), (12, 'Twelve Months'), (24, 'Twenty Four Months')], null=True)),
                ('room_type', models.TextField(blank=True, choices=[('1+kk', 'One Kk'), ('2+kk', 'Two Kk'), ('3+kk', 'Three Kk'), ('4+kk', 'Four Kk'), ('5+kk', 'Five Kk'), ('6+kk', 'Six Kk'), ('1+1', 'One One'), ('2+1', 'Two One'), ('3+1', 'Three One'), ('4+1', 'Four One'), ('5+1', 'Five One'), ('6+1', 'Six One'), ('other', 'Other')], null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommuteType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FacilityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LifestyleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='property',
            name='meters_squared',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='photo_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='room_type',
            field=models.TextField(blank=True, choices=[('1+kk', 'One Kk'), ('2+kk', 'Two Kk'), ('3+kk', 'Three Kk'), ('4+kk', 'Four Kk'), ('5+kk', 'Five Kk'), ('6+kk', 'Six Kk'), ('1+1', 'One One'), ('2+1', 'Two One'), ('3+1', 'Three One'), ('4+1', 'Four One'), ('5+1', 'Five One'), ('6+1', 'Six One'), ('other', 'Other')], null=True),
        ),
        migrations.AddField(
            model_name='propertyrentals',
            name='length_of_stay',
            field=models.IntegerField(blank=True, choices=[(3, 'Three Months'), (6, 'Six Months'), (12, 'Twelve Months'), (24, 'Twenty Four Months')], null=True),
        ),
        migrations.CreateModel(
            name='LifestyleTypeProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lifestyle_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.lifestyletype')),
                ('property', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.property')),
            ],
        ),
        migrations.CreateModel(
            name='LifestyleTypeApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.application')),
                ('lifestyle_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.lifestyletype')),
            ],
        ),
        migrations.CreateModel(
            name='FacilityTypeProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facility_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.facilitytype')),
                ('property', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.property')),
            ],
        ),
        migrations.CreateModel(
            name='CommuteTypeApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.application')),
                ('commute_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.commutetype')),
            ],
        ),
        migrations.AddField(
            model_name='application',
            name='commute_types',
            field=models.ManyToManyField(related_name='applications', through='graphql_api.CommuteTypeApplication', to='graphql_api.CommuteType'),
        ),
        migrations.AddField(
            model_name='application',
            name='lifestyle_types',
            field=models.ManyToManyField(related_name='applications', through='graphql_api.LifestyleTypeApplication', to='graphql_api.LifestyleType'),
        ),
        migrations.AddField(
            model_name='application',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='property',
            name='facility_types',
            field=models.ManyToManyField(related_name='properties', through='graphql_api.FacilityTypeProperty', to='graphql_api.FacilityType'),
        ),
        migrations.AddField(
            model_name='property',
            name='lifestyle_types',
            field=models.ManyToManyField(related_name='properties', through='graphql_api.LifestyleTypeProperty', to='graphql_api.LifestyleType'),
        ),
        migrations.AddField(
            model_name='property',
            name='property_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.propertytype'),
        ),
    ]
