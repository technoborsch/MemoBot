import os


TOKEN = os.getenv('TOKEN')
if not TOKEN:
    from supersecret import MY_TOKEN
    TOKEN = MY_TOKEN

MAPS_KEY = os.getenv('MAPS_KEY')
if not MAPS_KEY:
    from supersecret import MY_MAPS
    MAPS_KEY = MY_MAPS

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
port = os.getenv('PORT')
if port:
    WEBAPP_PORT = port
else:
    WEBAPP_PORT = None
