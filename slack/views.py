from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from games.models import Game, Player

from .models import Team


MISSING_TEAM = "Oh dear. Your slack team isn't registered with TINTG. I'm... I'm not even sure how you reached us."

HELLO = "Hey there!"

HOW_TO_START = "You can start a game of tic-tac-toe with `/tintg tictac [username]`"

GAME_ALREADY_STARTED = "There's already a game going in this channel, sorry."

ERROR = "Hmm... something has gone wrong. Maybe try starting a new game?"

WRONG_TURN = "Whoops! It's not your turn to play."

INVALID_MOVE = "Sorry, that's not a valid move."

TICTAC_HELP = """`/tintg tictac [username]` - starts a new game\n`/tintg tictac move [space]` - play in an empty space\n`/tintg tictac show` - show current board state\n`/tintg tictac forfeit` - leave a game you're playing\n`/tintg tictac help` - display this help"""

BAD_PLAYER_NAME = "Hmm... that doesn't seem to be a valid player name."


@csrf_exempt
def slash_command(request):

    if request.method == 'GET':
        return render(
            request=request,
            template_name='slash_command.html'
        )

    if request.method == 'POST':
        try:
            team = Team.objects.get(token=request.POST.get('token'))
        except Team.DoesNotExist:
            return JsonResponse({
                'text': MISSING_TEAM,
            })
        command_text = request.POST.get('text')
        if command_text.startswith('tictac'):
            command_options = command_text.split(' ')
            # /tintg tictac
            if len(command_options) < 2:
                return JsonResponse({
                    'text': HOW_TO_START
                })
            game = None
            try:
                game = Game.objects.get(
                    channel=request.POST.get('channel_id'),
                    is_active=True,
                )
            except Game.DoesNotExist:
                pass
            # /tintg tictac show
            if command_options[1] == 'show' and game:
                try:
                    current_player = Player.objects.get(
                        game=game,
                        is_current=True,
                    )
                except Player.DoesNotExist:
                    return JsonResponse({
                        'text': ERROR,
                    })
                return JsonResponse({
                    'response_type': 'in_channel',
                    'text': "It is {}'s turn.".format(current_player),
                    'attachments': [
                        {'text': game.board_state_to_slack()},
                    ]
                })
            # /tintg tictac forfeit
            if command_options[1] in ('forfeit', 'quit') and game:
                player1, player2 = get_players(game, request.POST)
                if not player1 or not player2:
                    return JsonResponse({
                        'text': ERROR,
                    })
                game.is_active = False
                game.save()
                return JsonResponse({
                    'response_type': 'in_channel',
                    'text': "{} forfeits! {} wins the game!".format(
                        player1, player2,
                    )
                })
            # /tintg tictac help
            if command_options[1] == 'help':
                return JsonResponse({
                    'text': "Help for tic-tac-toe",
                    'attachments': [{
                        'text': TICTAC_HELP,
                        'mrkdwn_in': ["text"],
                    }],
                })
            # /tintg tictac move {move}
            if command_options[1] == 'move' and game:
                player1, player2 = get_players(game, request.POST)
                if not player1 or not player2:
                    return JsonResponse({
                        'text': ERROR,
                    })
                if not player1.is_current:
                    return JsonResponse({
                        'text': WRONG_TURN
                    })
                valid = game.make_move_if_valid(' '.join(command_options[2:]))
                if valid:
                    if game.is_won():
                        game.is_active = False
                        game.save()
                        return JsonResponse({
                            'response_type': 'in_channel',
                            'text': "{} has won the game!".format(player1),
                            'attachments': [{
                                'text': game.board_state_to_slack(),
                            }]
                        })
                    player1.is_current = False
                    player1.save()
                    player2.is_current = True
                    player2.save()
                    return JsonResponse({
                        'response_type': 'in_channel',
                        'text': "{} has played. It's {}'s turn now.".format(
                            player1, player2,
                        ),
                        'attachments': [
                            {'text': game.board_state_to_slack()}
                        ]
                    })
                else:
                    return JsonResponse({
                        'text': INVALID_MOVE,
                    })
            # /tintg tictac {username}
            else:
                if game:
                    return JsonResponse({
                        'text': GAME_ALREADY_STARTED
                    })
                if len(command_options) > 2:
                    return JsonResponse({
                        'text': BAD_PLAYER_NAME
                    })
                game = Game.objects.start_game(
                    kind=str(Game.TICTACTOE),
                    channel=request.POST.get('channel_id'),
                )
                player1 = Player.objects.create(
                    game=game,
                    name=request.POST.get('user_name').strip('@'),
                    is_current=True,
                    remote_user_id=request.POST.get('user_id'),
                )
                player2 = Player.objects.create(
                    game=game,
                    name=command_options[1].strip('@'),
                )
                return JsonResponse({
                    'response_type': 'in_channel',
                    'text': "{} has challenged {} to TicTacToe! It is {}'s turn.".format(
                        player1, 
                        player2,
                        player1,
                    ),
                    'attachments': [
                        {'text': game.board_state_to_slack()}
                    ]
                })

        if command_text.lower() == 'hello':
            return JsonResponse({
                'text': HELLO,
            })
        return JsonResponse({
            'text': HOW_TO_START,
            'mrkdwn': True,
        })

def get_players(game, command_data):
    player1 = None,
    player2 = None
    players = Player.objects.filter(game=game)
    try:
        player1 = players.get(
            name=command_data.get('user_name').strip('@'),
        )
        player1.remote_user_id = command_data.get('user_id')
        player1.save()
    except Player.DoesNotExist:
        try:
            player1 = players.get(
                remote_user_id=command_data.get('user_id'),
            )
        except Player.DoesNotExist:
            pass
    try:
        player2 = players.get(is_current=False)
    except Player.DoesNotExist:
        pass

    return player1, player2
