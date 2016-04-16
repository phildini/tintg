import factory
 
from . import models


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Team

    token = "cal-stewart-hender-field"
    name = "Slack"
    slack_id = "T0001"
    domain = "slack"