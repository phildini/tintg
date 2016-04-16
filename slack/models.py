from django.db import models


class Team(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slack_id = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255)

    def __str__(self):
        return "{} ({})".format(self.name, self.id)
