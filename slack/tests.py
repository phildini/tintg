import json
from django.test import TestCase
from django.test.client import RequestFactory
from games.factories import (
    GameFactory,
    PlayerFactory,
)
from games.models import Game
from . import factories
from . import views


class SlashCommandTests(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.team = factories.TeamFactory.create()

    def make_command_request(self, command_option_string, username, channel):
        return self.request_factory.post(
            '/slack/',
            {
                'token': self.team.token,
                'team_id': self.team.slack_id,
                'team_domain': self.team.domain,
                'channel_id': '%s' % channel,
                'channel_name': 'general',
                'user_id': 'U12345',
                'user_name': '%s' % username,
                'command': '/tintg',
                'text': '%s' % command_option_string,
                'response_url': 'https://hooks.slack.com/commands/1234/5678',
            },
        )

    def test_basic_get_request(self):
        request = self.request_factory.get('/slack/')
        response = views.slash_command(request)
        self.assertEqual(response.status_code, 200)

    def test_basic_post_request(self):
        request = self.make_command_request('hello', 'Stewart', 'C12345')
        response = views.slash_command(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "text": views.HELLO
        })

    def test_basic_request_bad_team(self):
        request = self.request_factory.post(
            '/slack/',
            {
                'token': '12345',
                'team_id': '098765',
                'team_domain': 'hipchat',
                'channel_id': 'C12345',
                'channel_name': 'general',
                'user_id': 'U12345',
                'user_name': 'Stewart',
                'command': '/tintg',
                'text': 'hello',
                'response_url': 'https://hooks.slack.com/commands/1234/5678',
            },
        )
        response = views.slash_command(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "text": views.MISSING_TEAM
        })

    def test_tictac_no_player(self):
        request = self.make_command_request('tictac', 'Stewart', 'C12345')
        response = views.slash_command(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'text': views.HOW_TO_START,
        })

    def test_tictac_already_channel(self):
        game = GameFactory.create(channel='C98765')
        request = self.make_command_request('tictac @cal', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'text': views.GAME_ALREADY_STARTED,
        })

    def test_tictac_new_game(self):
        request = self.make_command_request('tictac @cal', 'Stewart', 'C12345')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'response_type': 'in_channel',
            'text': "Stewart has challenged cal to TicTacToe! It is Stewart's turn.",
            'attachments': [
                {
                    'text': ":white_medium_square: :white_medium_square: :white_medium_square: \n:white_medium_square: :white_medium_square: :white_medium_square: \n:white_medium_square: :white_medium_square: :white_medium_square: "
                }
            ]
        })

    def test_tictac_good_move(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [[0,0,0],[0,0,0],[0,0,0]]
        }
        game.save()
        player1 = PlayerFactory.create(
            game=game,
            name='Stewart',
            is_current=True,
        )
        player2 = PlayerFactory.create(game=game, name='cal')
        request = self.make_command_request('tictac move 3', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'response_type': 'in_channel',
            'text': "Stewart has played. It's cal's turn now.",
            'attachments': [
                {
                    'text': ":white_medium_square: :white_medium_square: :x: \n:white_medium_square: :white_medium_square: :white_medium_square: \n:white_medium_square: :white_medium_square: :white_medium_square: "
                }
            ]
        })

    def test_tictac_bad_move(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [[0,0,0],[0,0,0],[0,0,0]]
        }
        game.save()
        player1 = PlayerFactory.create(
            game=game,
            name='Stewart',
            is_current=True,
        )
        player2 = PlayerFactory.create(game=game, name='cal')
        request = self.make_command_request('tictac move 3', 'cal', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'text': views.WRONG_TURN,
        })

    def test_tictac_win(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [[0,'X',0],[0,'X',0],[0,0,0]]
        }
        game.save()
        player1 = PlayerFactory.create(
            game=game,
            name='Stewart',
            is_current=True,
        )
        player2 = PlayerFactory.create(game=game, name='cal')
        request = self.make_command_request('tictac move 8', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'response_type': 'in_channel',
            'text': 'Stewart has won the game!',
            'attachments': [{
                'text': ":white_medium_square: :x: :white_medium_square: \n:white_medium_square: :x: :white_medium_square: \n:white_medium_square: :x: :white_medium_square: "
            }]
        })

    def test_tictac_invalid_move(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [[0,'X',0],[0,'X',0],[0,0,0]]
        }
        game.save()
        player1 = PlayerFactory.create(
            game=game,
            name='Stewart',
            is_current=True,
        )
        player2 = PlayerFactory.create(game=game, name='cal')
        request = self.make_command_request('tictac move 5', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'text': views.INVALID_MOVE
        })

    def test_tictac_move_no_players(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [[0,'X',0],[0,'X',0],[0,0,0]]
        }
        game.save()
        request = self.make_command_request('tictac move 5', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'text': views.ERROR
        })

    def test_tictac_display(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [['X',0,0],[0,'X',0],[0,0,'O']]
        }
        game.save()
        player1 = PlayerFactory.create(
            game=game,
            name='Stewart',
            is_current=True,
        )
        player2 = PlayerFactory.create(game=game, name='cal')
        request = self.make_command_request('tictac show', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'response_type': 'in_channel',
            'text': "It is Stewart's turn.",
            'attachments': [
                {
                    'text': ":x: :white_medium_square: :white_medium_square: \n:white_medium_square: :x: :white_medium_square: \n:white_medium_square: :white_medium_square: :o: "
                }
            ]
        })

    def test_tictac_show_no_players(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [['X',0,0],[0,'X',0],[0,0,'O']]
        }
        game.save()
        request = self.make_command_request('tictac show', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'text': views.ERROR,
        })

    def test_tictac_forfeit(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [['X',0,0],[0,'X',0],[0,0,'O']]
        }
        game.save()
        player1 = PlayerFactory.create(
            game=game,
            name='Stewart',
            is_current=True,
        )
        player2 = PlayerFactory.create(game=game, name='cal')
        request = self.make_command_request('tictac forfeit', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'response_type': 'in_channel',
            'text': "Stewart forfeits! cal wins the game!",
        })
        game = Game.objects.get(id=game.id)
        self.assertFalse(game.is_active)

    def test_tictac_forfeit_no_players(self):
        game = GameFactory.create(channel='C98765')
        game.state = {
            'last_move': 'O',
            'board': [['X',0,0],[0,'X',0],[0,0,'O']]
        }
        game.save()
        request = self.make_command_request('tictac forfeit', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'text': views.ERROR,
        })

    def test_tictac_help(self):
        request = self.make_command_request('tictac help', 'Stewart', 'C98765')
        response = views.slash_command(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'text': "Help for tic-tac-toe",
            'attachments': [{ 
                'text': views.TICTAC_HELP, 
                'mrkdwn_in': ["text"], 
            }], 
        })

