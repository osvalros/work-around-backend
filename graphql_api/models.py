from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Property(models.Model):
    coordinates = models.PointField()
    user = models.ForeignKey(User, models.CASCADE)
