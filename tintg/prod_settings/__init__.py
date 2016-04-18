import dj_database_url
from tintg.settings import *

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES['default'] = dj_database_url.parse(get_env_variable('TINTG_DB_URL'))

SECRET_KEY = get_env_variable('TINTG_SECRET_KEY')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.herokuapp.com',
]

SECURE_HSTS_SECONDS = 3600
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

INSTALLED_APPS += (
    'gunicorn',
    'opbeat.contrib.django',
)

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
) + MIDDLEWARE_CLASSES

OPBEAT = {
    'ORGANIZATION_ID': get_env_variable("OPBEAT_ORG_ID"),
    'APP_ID': get_env_variable("OPBEAT_APP_ID"),
    'SECRET_TOKEN': get_env_variable("OPBEAT_SECRET_KEY"),
}