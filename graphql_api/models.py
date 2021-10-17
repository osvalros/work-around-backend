from typing import List, Union

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.db import transaction

from graphql_api.utils import pairwise


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


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    coordinates = models.PointField(geography=True, null=True, blank=True)

    class Meta:
        unique_together = ("name", "country")


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Application(models.Model):
    property = models.ForeignKey("Property", models.CASCADE, related_name="applications")
    pet_friendly = models.BooleanField(blank=True, null=True)
    move_in_date = models.DateField(blank=True, null=True)
    length_of_stay = models.IntegerField(choices=LengthOfStay.choices)
    accepted = models.BooleanField(default=False)
    lifestyle_types = models.ManyToManyField("graphql_api.LifestyleType", through="LifestyleTypeApplication",
                                             related_name="applications")
    commute_types = models.ManyToManyField("graphql_api.CommuteType", through="CommuteTypeApplication",
                                           related_name="applications")
    facility_types = models.ManyToManyField("graphql_api.FacilityType", through="FacilityTypeApplication",
                                            related_name="applications")
    property_types = models.ManyToManyField("graphql_api.PropertyType", through="PropertyTypeApplication",
                                            related_name="applications")
    preferred_cities = models.ManyToManyField(City, through="ApplicationPreferredCity",
                                              related_name="applications")
    recommendations = models.ManyToManyField("Recommendation", through="RecommendationApplication",
                                             related_name="applications")


class ApplicationPreferredCity(models.Model):
    application = models.ForeignKey(Application, models.CASCADE)
    city = models.ForeignKey(City, models.CASCADE)
    order = models.IntegerField()


class LifestyleType(models.Model):
    name = models.TextField()


class LifestyleTypeApplication(models.Model):
    lifestyle_type = models.ForeignKey(LifestyleType, models.SET_NULL, blank=True, null=True)
    application = models.ForeignKey(Application, models.SET_NULL, blank=True, null=True)


class PropertyType(models.Model):
    name = models.TextField()


class FacilityType(models.Model):
    name = models.TextField()


class CommuteType(models.Model):
    name = models.TextField()


class CommuteTypeApplication(models.Model):
    commute_type = models.ForeignKey(CommuteType, models.SET_NULL, blank=True, null=True)
    application = models.ForeignKey(Application, models.SET_NULL, blank=True, null=True)


class FacilityTypeApplication(models.Model):
    facility_type = models.ForeignKey(FacilityType, models.CASCADE)
    application = models.ForeignKey(Application, models.CASCADE)


class PropertyTypeApplication(models.Model):
    property_type = models.ForeignKey(PropertyType, models.CASCADE)
    application = models.ForeignKey(Application, models.CASCADE)


class Property(models.Model):
    coordinates = models.PointField(geography=True)
    user = models.ForeignKey(User, models.CASCADE, related_name="properties")
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_available = models.BooleanField(default=False)
    usd_worth = models.FloatField()
    photo_id = models.CharField(max_length=50)
    meters_squared = models.IntegerField()
    property_type = models.ForeignKey(PropertyType, models.SET_NULL, blank=True, null=True)
    room_type = models.TextField(choices=RoomType.choices, blank=True, null=True)
    facility_types = models.ManyToManyField("graphql_api.FacilityType", through="FacilityTypeProperty",
                                            related_name="properties")
    lifestyle_types = models.ManyToManyField("graphql_api.LifestyleType", through="LifestyleTypeProperty",
                                             related_name="properties")
    city = models.ForeignKey(City, models.SET_NULL, blank=True, null=True, related_name="properties")


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


class RecommendationManager(models.Manager):
    @transaction.atomic
    def create_recommendation(self, application_ids: List[Union[str, int]]):
        if len(application_ids) < 2:
            raise Exception("At least 2 application ids needed for a recommendation.")
        recommendation = self.create()
        recommendation_applications = [
            RecommendationApplication.objects.create(application_id=application_id, recommendation=recommendation)
            for application_id in application_ids
        ]
        for recommendation_application, next_recommendation_application in pairwise(recommendation_applications):
            recommendation_application.recommended = next_recommendation_application
            recommendation_application.save()
        recommendation_applications[-1].recommended = recommendation_applications[0]
        recommendation_applications[-1].save()

        return recommendation


class Recommendation(models.Model):
    objects = RecommendationManager()

    accepted = models.BooleanField(default=False)


class RecommendationApplication(models.Model):
    recommendation = models.ForeignKey(Recommendation, models.CASCADE, related_name="recommendation_applications")
    application = models.ForeignKey(Application, models.CASCADE, related_name="recommendation_applications")
    recommended = models.ForeignKey("RecommendationApplication", models.CASCADE, null=True, blank=True)
    accepted = models.BooleanField(default=False)

    @transaction.atomic
    def accept(self):
        self.accepted = True
        self.save()
        if self.recommendation.recommendation_applications.filter(accepted=False).exists():
            return
        self.recommendation.accepted = True
        self.recommendation.save()

        applications_of_recommendation = \
            Application.objects.filter(recommendation_applications__recommendation=self.recommendation)
        applications_of_recommendation.update(accepted=True)

        Recommendation.objects.exclude(id=self.recommendation.id) \
            .filter(recommendation_applications__application_id__in=applications_of_recommendation.values_list("id", flat=True)) \
            .delete()

    class Meta:
        unique_together = ("recommendation", "application")

