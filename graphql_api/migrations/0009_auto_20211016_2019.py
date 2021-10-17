# Generated by Django 3.2.8 on 2021-10-16 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graphql_api', '0008_auto_20211016_1943'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'unique_together': {('name', 'country')},
            },
        ),
        migrations.CreateModel(
            name='ApplicationPreferredCity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='graphql_api.application')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='graphql_api.city')),
            ],
        ),
        migrations.AddField(
            model_name='application',
            name='preferred_cities',
            field=models.ManyToManyField(to='graphql_api.City'),
        ),
        migrations.AddField(
            model_name='property',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='graphql_api.city'),
        ),
    ]
