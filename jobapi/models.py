from django.db import models

class JobOffer(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    sector = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    salary_min = models.FloatField()
    salary_max = models.FloatField()
    skills_extracted_list = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.company}"
