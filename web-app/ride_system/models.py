from django.db import models
from django.contrib.auth.models import User


class Driver(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
    drivername = models.CharField(max_length=200)
    car_type = models.CharField(max_length=200)
    plate_number = models.CharField(max_length=200)
    capacity = models.IntegerField()
    special = models.CharField(max_length=200, blank=True, null=True)

class SharePart(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.IntegerField()

class Trip(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_trips')
    destination = models.CharField(max_length=200)
    date = models.DateTimeField()
    number = models.IntegerField()
    car_type = models.CharField(max_length=200)
    special = models.CharField(max_length=200)
    isShared = models.BooleanField()
    # can not be seen from request
    shareSet = models.ManyToManyField(SharePart, blank=True)
    isConfirmed = models.BooleanField(default=False)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    isComplete = models.BooleanField(default=False)
    