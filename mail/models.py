from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Mail(models.Model):
    mailId = models.CharField(max_length=255)
    snippet = models.CharField(max_length=1000)
