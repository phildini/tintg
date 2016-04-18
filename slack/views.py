from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from games.models import Game, Player

from .models import Team


MISSING_TEAM = "Oh dear. Your slack team isn't registered with TINTG. I'm... I'm not even sure how you reached us."

HELLO = "Hey there!"

HOW_TO_START = "You can start a game of tic-tac-toe with `/tintg tictac {username}`"

GAME_ALREADY_STARTED = "There's already a game going in this channel, sorry."

ERROR = "Hmm... something has gone wrong. Maybe try starting a new game?"

WRONG_TURN = "Whoops! It's not your turn to play."

INVALID_MOVE = "Sorry, that's not a valid move."

TICTAC_HELP = """`/tintg tictac [username]` - starts a new game\n`/tintg tictac move [space]` - play in an empty space\n`/tintg tictac show` - show current board state\n`/tintg tictac forfeit` - leave a game you're playing\n`/tintg tictac help` - display this help"""


@csrf_exempt
def slash_command(request):

    if request.method == 'POST':
        try:
            team = Team.objects.get(slack_id=request.POST.get('team_id'))
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
            else:
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
                    players = Player.objects.filter(game=game)
                    try:
                        current_player = Player.objects.get(
                            game=game,
                            name=request.POST.get('user_name')
                        )
                    except Player.DoesNotExist:
                        try:
                            current_player = Player.objects.get(
                                game=game,
                                remote_user_id=request.POST.get('user_id')
                            )
                        except Player.DoesNotExist:
                            return JsonResponse({
                                'text': ERROR,
                            })
                    other_player = players.exclude(id=current_player.id)[0]
                    game.is_active = False
                    game.save()
                    return JsonResponse({
                        'response_type': 'in_channel',
                        'text': "{} forfeits! {} wins the game!".format(
                            current_player, other_player,
                        )
                    })
                # /tintg tictac help
                if command_options[1] == 'help':
                    return JsonResponse({
                        'text': "Help for tic-tac-toe",
                        'attachments': [{'text': TICTAC_HELP}],
                    })
                # /tintg tictac move {move}
                if command_options[1] == 'move' and game:
                    players = Player.objects.filter(game=game)
                    try:
                        player1 = players.get(
                            name=request.POST.get('user_name').strip('@'),
                        )
                    except Player.DoesNotExist:
                        try:
                            player1 = players.get(
                                remote_user_id=request.POST.get('user_id'),
                            )
                        except Player.DoesNotExist:
                            return JsonResponse({
                                'text': ERROR,
                            })
                    try:
                        player2 = players.get(is_current=False)
                    except Player.DoesNotExist:
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
                            return JsonResponse({
                                'response_type': 'in_channel',
                                'text': "{} has won the game!".format(player1)
                            })
                        player2 = players.get(is_current=False)
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
                            player1, player2, player1,
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


