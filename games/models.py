import collections
from django.db import models
from jsonfield import JSONField


class Player(models.Model):

    game = models.ForeignKey('Game')
    name = models.CharField(max_length=100, blank=True)
    is_current = models.BooleanField(default=False)
    remote_user_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        if self.name:
            return self.name
        if self.remote_user_id:
            return self.remote_user_id
        return "Player"


class GameManager(models.Manager):

    def start_game(self, kind, channel):
        game = self.create(kind=kind, channel=channel, is_active=True)
        if kind == Game.TICTACTOE:
            game.state = {
                'last_move': 'O',
                'board': [[0,0,0],[0,0,0],[0,0,0]]
            }
            game.save()
        return game


class Game(models.Model):
    TICTACTOE = 'tictactoe'

    MOVE_OPTIONS = {
        1: ['upper left', 'top left', 'top left corner', 'upper left corner'],
        2: ['top mid', 'top middle', 'upper mid', 'upper middle'],
        3: ['top right', 'upper right', 'top right corner', 'upper right corner'],
        4: ['middle left', 'mid left', 'center left'],
        5: ['middle middle', 'middle', 'center'],
        6: ['middle right', 'center right', 'mid right'],
        7: ['bottom left', 'bot left', 'bot left corner', 'lower left', 'lower left corner', 'bottom left corner'],
        8: ['bottom middle', 'bot middle', 'bot middle', 'lower middle', 'lower mid', 'bottom mid', 'bot mid'],
        9: ['bottom right', 'bot right', 'bot right corner', 'lower right', 'lower right corner', 'bottom right corner'],
    }

    GAME_TYPES = (
        (TICTACTOE, "Tic-tac-toe"),
    )

    kind = models.CharField(max_length=100, choices=GAME_TYPES)
    state = JSONField(
        load_kwargs={'object_pairs_hook': collections.OrderedDict},
    )
    channel = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False)

    objects = GameManager()

    def board_state_to_slack(self):
        text = ""
        board = self.state.get('board')
        for index, row in enumerate(board):
            for space in row:
                if space == 0:
                    text += ':white_medium_square: '
                if space == 'X':
                    text += ':x: '
                if space == 'O':
                    text += ':o: '
            if index < 2:
                text += '\n'
        return text

    def make_move_if_valid(self, move):
        board = self.state.get('board')
        last_move = self.state.get('last_move')
        move = move.lower()
        is_valid = False
        if last_move == 'O':
            piece = 'X'
        else:
            piece = 'O'
        if move == '1' or move in self.MOVE_OPTIONS[1]:
            if board[0][0] == 0:
                is_valid = True
                board[0][0] = piece
                last_move = piece
        if move == '2' or move in self.MOVE_OPTIONS[2]:
            if board[0][1] == 0:
                is_valid = True
                board[0][1] = piece
                last_move = piece
        if move == '3' or move in self.MOVE_OPTIONS[3]:
            if board[0][2] == 0:
                is_valid = True
                board[0][2] = piece
                last_move = piece
        if move == '4' or move in self.MOVE_OPTIONS[4]:
            if board[1][0] == 0:
                is_valid = True
                board[1][0] = piece
                last_move = piece
        if move == '5' or move in self.MOVE_OPTIONS[5]:
            if board[1][1] == 0:
                is_valid = True
                board[1][1] = piece
                last_move = piece
        if move == '6' or move in self.MOVE_OPTIONS[6]:
            if board[1][2] == 0:
                is_valid = True
                board[1][2] = piece
                last_move = piece
        if move == '7' or move in self.MOVE_OPTIONS[7]:
            if board[2][0] == 0:
                is_valid = True
                board[2][0] = piece
                last_move = piece
        if move == '8' or move in self.MOVE_OPTIONS[8]:
            if board[2][1] == 0:
                is_valid = True
                board[2][1] = piece
                last_move = piece
        if move == '9' or move in self.MOVE_OPTIONS[9]:
            if board[2][2] == 0:
                is_valid = True
                board[2][2] = piece
                last_move = piece
        self.state['board'] = board
        self.state['last_move'] = last_move
        self.save()
        return is_valid

    def is_won(self):
        board = self.state.get('board')
        row_tie = False
        # check rows
        for row in board:
            if len(set(row)) == 1:
                row_tie = False
                if list(set(row))[0] != 0:
                    return True
            elif not 0 in list(set(row)):
                    row_tie = True
        # check columns
        column_tie = False
        column_sets = [
            set([board[0][0], board[1][0], board[2][0]]),
            set([board[0][1], board[1][1], board[2][1]]),
            set([board[0][2], board[1][2], board[2][2]]),
        ]
        for column in column_sets:
            if len(column) == 1:
                if list(column)[0] != 0:
                    return True
            elif 0 not in list(column):
                column_tie = True
        # check diagonals
        diagonal_tie = False
        diagonal_sets = [
            set([board[0][0], board[1][1], board[2][2]]),
            set([board[0][2], board[1][1], board[2][0]]),
        ]
        for diagonal in diagonal_sets:
            if len(diagonal) == 1:
                if list(diagonal)[0] != 0:
                    return True
            elif not 0 in list(diagonal):
                diagonal_tie = True
        if row_tie and column_tie and diagonal_tie:
            return 'tie'
        return False

