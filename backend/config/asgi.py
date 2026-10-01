
# external libraries imports
import os
from django.core.asgi import get_asgi_application

# main code
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
