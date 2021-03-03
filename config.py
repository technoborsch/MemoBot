import os


TOKEN = os.getenv('TOKEN')
if not TOKEN:
    print('You have forgot to set BOT_TOKEN')
    quit()

MAPS_KEY = os.getenv('MAPS_KEY')
if not MAPS_KEY:
    print("No map key")
    quit()

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT'))
