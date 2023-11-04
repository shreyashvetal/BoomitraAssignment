from django.db import models

# Create your models here.

class Polygon(models.Model):
    name = models.CharField(max_length=100)
    geojson = models.TextField()