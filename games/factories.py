import factory
from . import models


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Game

    kind = models.Game.TICTACTOE
    channel = 'C12345'
    is_active = True


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Player

    game = factory.SubFactory(GameFactory)
    name = 'stewart'
    remote_user_id = 'U12345'