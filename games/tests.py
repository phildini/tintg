from django.test import TestCase
from .factories import GameFactory
from .models import Game


class GameModelTests(TestCase):

    def test_each_move(self):
        for i in range(1, 10):
            game = Game.objects.start_game(kind=Game.TICTACTOE, channel='test')
            self.assertTrue(game.make_move_if_valid(str(i)))
            for move in Game.MOVE_OPTIONS[i]:
                game = Game.objects.start_game(
                    kind=Game.TICTACTOE, channel='test',
                )
                self.assertTrue(game.make_move_if_valid(move))
            for move in Game.MOVE_OPTIONS[i]:
                game = Game.objects.create(
                    kind=Game.TICTACTOE,
                    channel='test',
                    state={
                        'board': [['O','O','O'],['O','O','O'],['O','O','O']],
                    },
                )
                self.assertFalse(game.make_move_if_valid(move))

    def test_wins(self):
        board = [['X','X','X'],[0,0,0],[0,0,0]]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board': board},
        )
        self.assertTrue(game.is_won())
        board = [[0,0,0],['X','X','X'],[0,0,0]]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board': board},
        )
        self.assertTrue(game.is_won())
        board = [[0,0,0],[0,0,0],['X','X','X']]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertTrue(game.is_won())
        board = [['X',0,0],['X',0,0],['X',0,0]]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertTrue(game.is_won())
        board = [[0,'X',0],[0,'X',0],[0,'X',0]]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertTrue(game.is_won())
        board = [[0,0,'X'],[0,0,'X'],[0,0,'X']]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertTrue(game.is_won())
        board = [['X',0,0],[0,'X',0],[0,0,'X']]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertTrue(game.is_won())
        board = [[0,0,'X'],[0,'X',0],['X',0,0]]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertTrue(game.is_won())
        board = [[0,0,'X'],[0,'X',0],[0,0,0]]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertFalse(game.is_won())
        board = [['X',0,0],[0,0,0],[0,0,0]]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertFalse(game.is_won())
        board = [[0,0,0],[0,0,0],[0,0,0]]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertFalse(game.is_won())
        board = [['X','O','X'],['X','O','O'],['O','X','X']]
        game = Game.objects.create(
            kind=Game.TICTACTOE,
            channel='test',
            state={'board':board},
        )
        self.assertEqual(game.is_won(), 'tie')


