from django.db import models

# Create your models here.
class FooMessage(models.Model):
    message_text = models.CharField(max_length=200)
    is_active = models.BooleanField()
