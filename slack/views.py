from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Team


MISSING_TEAM = "Oh dear. Your slack team isn't registered with TINTG. I'm... I'm not even sure how you reached us."

HELLO = "Hey there!"



@csrf_exempt
def slash_command(request):

    if request.method == 'POST':
        try:
            team = Team.objects.get(slack_id=request.POST.get('team_id'))
        except Team.DoesNotExist:
            return JsonResponse({
                'text': MISSING_TEAM,
            })
        return JsonResponse({
            'text': HELLO,
        })


