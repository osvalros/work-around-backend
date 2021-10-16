from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Property(models.Model):
    coordinates = models.PointField(geography=True)
    user = models.ForeignKey(User, models.CASCADE)
    is_available = models.BooleanField(default=False)
    usd_worth = models.FloatField()


class PropertyRentals(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    property = models.ForeignKey(Property, models.SET_NULL, blank=True, null=True)
