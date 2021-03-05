import os


TOKEN = os.getenv('TOKEN')
if not TOKEN:
    TOKEN = "1661220093:AAG6tVi2oIkVmSVqBE5mRILOINBgWwOatFk"

MAPS_KEY = os.getenv('MAPS_KEY')
if not MAPS_KEY:
    MAPS_KEY = "AIzaSyCHQTnatWz9-Mm5zTsZGEtjYDNTApZ0h5M"

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
port = os.getenv('PORT')
if port:
    WEBAPP_PORT = int(os.getenv('PORT'))
else:
    WEBAPP_PORT = None
