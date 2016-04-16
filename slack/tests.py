import json
from django.test import TestCase
from django.test.client import RequestFactory
from . import factories
from . import views


class SlashCommandTests(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.team = factories.TeamFactory.create()

    def test_basic_request(self):
        request = self.request_factory.post(
            '/slack/',
            {
                'token': self.team.token,
                'team_id': self.team.slack_id,
                'team_domain': self.team.domain,
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


