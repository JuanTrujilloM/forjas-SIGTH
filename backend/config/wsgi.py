
# external libraries imports
import os
from django.core.wsgi import get_wsgi_application

# main code
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
