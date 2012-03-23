from django.db import models

class Announcement(models.Model):
    PRIOIRTY_CHOICES = (
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    )
    announcement_id = models.AutoField(primary_key=True)
    announcement_text = models.CharField(max_length=64)
    priority = models.CharField(max_length=1, choices=PRIOIRTY_CHOICES)
    is_active = models.BooleanField()
    creation_date = models.DateTimeField()