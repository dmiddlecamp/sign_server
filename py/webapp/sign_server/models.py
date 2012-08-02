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

class BoardLease(models.Model):
    board_lease_id = models.AutoField(primary_key=True)
    board_lease_code = models.CharField(max_length=32)
    is_active = models.BooleanField()
    current_color = models.TextField(max_length=1, default=chr(29))
    top_row = models.IntegerField(max_length=2)
    left_col = models.IntegerField(max_length=2)
    bottom_row = models.IntegerField(max_length=2)
    right_col = models.IntegerField(max_length=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    creation_date = models.DateTimeField()
