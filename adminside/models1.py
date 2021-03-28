from math import trunc
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db.models.deletion import CASCADE
from UserAuth.models import User
import datetime
from datetime import tzinfo, timezone
# from django import forms


class PitStopModel (models.Model):
    name = models.CharField(
        max_length=80,)
    longitude = models.FloatField(max_length=600, blank=True, null=True)
    latitude = models.FloatField(max_length=600, null=True, blank=True)
    rating = models.FloatField(default=0, null=True, blank=True)
    city = models.CharField(max_length=600, null=True, blank=True)
    class Meta:
        db_table = 'PitStopModel'

    def __str__(self):
        return str(self.name)



class Locations (models.Model):
    # , related_name="PitStopModel" , on_delete=models.CASCADE
    # pit_stop = models.ForeignKey(PitStopModel, related_name="PitStopModel" , on_delete=models.CASCADE )
    # id = models.Field(primary_key=True)
    pit_stop = models.ManyToManyField( PitStopModel,related_name='new_key' , blank=True)
    name = models.CharField(max_length=80, blank=True, null=True)
    longitude = models.FloatField(max_length=600, blank=True, null=True)
    latitude = models.FloatField(max_length=600, null=True, blank=True)
    distance_stop = models.FloatField(max_length=600, null=True, blank=True)
    rating_stop = models.FloatField(null=True, blank=True)

    location_type = models.CharField(max_length=600, null=True, blank=True)
    city = models.CharField(max_length=600, null=True, blank=True)


class RecommendedLocationModal (models.Model):

    user = models.ForeignKey(
        User, default=0, on_delete=models.CASCADE)
    gener = models.CharField(max_length=600, blank=True)

    message = models.CharField(max_length=5000, blank=True, null=True)
    status = models.IntegerField(default=1)


class RecommendedPositionModal(models.Model):
    user = models.ForeignKey(User,  null=True,
                             blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=600, default=None)
    latitude = models.FloatField(max_length=600, default=None)
    longitude = models.FloatField(max_length=600, default=None)
    status = models.IntegerField(default=1)


class RecommendedPositionLocationModal(models.Model):
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=600, default=None)
    location_latitude = models.FloatField(max_length=600, default=None)
    location_longitude = models.FloatField(max_length=600, default=None)
    location_type = models.CharField(max_length=600, default='resturant')
    status = models.IntegerField(default=1)
    rating = models.IntegerField(default=0)



class RatingFeedbackModel (models.Model):
    class Meta:
        unique_together = (('user', 'location_id'))

    user = models.ForeignKey(
        User, default=0, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=600, null=True, blank=True)
    rating = models.CharField(max_length=600, null=True, blank=True)

    location_id = models.ForeignKey(
        Locations, default=0, on_delete=models.CASCADE)
    pit_stop_id = models.ForeignKey(
        PitStopModel, default=0, on_delete=models.CASCADE)
