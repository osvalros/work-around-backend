from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser


class LengthOfStay(models.IntegerChoices):
    THREE_MONTHS = 3
    SIX_MONTHS = 6
    TWELVE_MONTHS = 12
    TWENTY_FOUR_MONTHS = 24


class RoomType(models.TextChoices):
    ONE_KK = "1+kk"
    TWO_KK = "2+kk"
    THREE_KK = "3+kk"
    FOUR_KK = "4+kk"
    FIVE_KK = "5+kk"
    SIX_KK = "6+kk"
    ONE_ONE = "1+1"
    TWO_ONE = "2+1"
    THREE_ONE = "3+1"
    FOUR_ONE = "4+1"
    FIVE_ONE = "5+1"
    SIX_ONE = "6+1"
    OTHER = "other"


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Application(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    pet_friendly = models.BooleanField(blank=True, null=True)
    move_in_date = models.DateField(blank=True, null=True)
    length_of_stay = models.IntegerField(choices=LengthOfStay.choices, blank=True, null=True)
    room_type = models.TextField(choices=RoomType.choices, blank=True, null=True)
    lifestyle_types = models.ManyToManyField("graphql_api.LifestyleType", through="LifestyleTypeApplication",
                                             related_name="applications")
    commute_types = models.ManyToManyField("graphql_api.CommuteType", through="CommuteTypeApplication",
                                           related_name="applications")


class LifestyleType(models.Model):
    name = models.TextField(blank=True, null=True)


class LifestyleTypeApplication(models.Model):
    lifestyle_type = models.ForeignKey(LifestyleType, models.SET_NULL, blank=True, null=True)
    application = models.ForeignKey(Application, models.SET_NULL, blank=True, null=True)


class PropertyType(models.Model):
    name = models.TextField(blank=True, null=True)


class FacilityType(models.Model):
    name = models.TextField(blank=True, null=True)


class CommuteType(models.Model):
    name = models.TextField(blank=True, null=True)


class CommuteTypeApplication(models.Model):
    commute_type = models.ForeignKey(CommuteType, models.SET_NULL, blank=True, null=True)
    application = models.ForeignKey(Application, models.SET_NULL, blank=True, null=True)


class Property(models.Model):
    coordinates = models.PointField(geography=True)
    user = models.ForeignKey(User, models.CASCADE)
    is_available = models.BooleanField(default=False)
    usd_worth = models.FloatField()
    photo_id = models.IntegerField()
    meters_squared = models.IntegerField()
    property_type = models.ForeignKey(PropertyType, models.SET_NULL, blank=True, null=True)
    room_type = models.TextField(choices=RoomType.choices, blank=True, null=True)
    facility_types = models.ManyToManyField("graphql_api.FacilityType", through="FacilityTypeProperty",
                                            related_name="properties")
    lifestyle_types = models.ManyToManyField("graphql_api.LifestyleType", through="LifestyleTypeProperty",
                                             related_name="properties")


class FacilityTypeProperty(models.Model):
    facility_type = models.ForeignKey(FacilityType, models.SET_NULL, blank=True, null=True)
    property = models.ForeignKey(Property, models.SET_NULL, blank=True, null=True)


class PropertyRentals(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    property = models.ForeignKey(Property, models.SET_NULL, blank=True, null=True)
    length_of_stay = models.IntegerField(choices=LengthOfStay.choices, blank=True, null=True)


class LifestyleTypeProperty(models.Model):
    lifestyle_type = models.ForeignKey(LifestyleType, models.SET_NULL, blank=True, null=True)
    property = models.ForeignKey(Property, models.SET_NULL, blank=True, null=True)
