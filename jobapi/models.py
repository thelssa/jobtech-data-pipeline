from django.contrib.postgres.fields import ArrayField
from django.db import models

class JobOffer(models.Model):
    company = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    sector = models.CharField(max_length=64, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    salary_min = models.FloatField(blank=True, null=True)
    salary_max = models.FloatField(blank=True, null=True)
    skills = ArrayField(models.CharField(max_length=64), blank=True, default=list)

    def __str__(self):
        return f"{self.company or 'Unknown'} - {self.title or 'No Title'}"
