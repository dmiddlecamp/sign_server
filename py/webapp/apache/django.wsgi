import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

path = '/projects/sign_server/py'
if path not in sys.path:
 sys.path.append(path);

path = '/projects/sign_server/py/webapp'
if path not in sys.path:
 sys.path.append(path);

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
