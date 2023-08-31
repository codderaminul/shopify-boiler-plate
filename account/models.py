from django.db import models

# Create your models here.

class Plan(models.Model):
    level = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.IntegerField()
    price_id = models.CharField(max_length=200)