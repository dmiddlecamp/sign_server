from django.db import models

# Create your models here.
class Announcement(models.Model):
    announcement_text = models.CharField(max_length=78)
    is_active = models.BooleanField()
    created_date = models.DateTimeField()