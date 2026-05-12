import sys
sys.path.append('..')

from vercel_python_wsgi import make_wsgi_app
import app as user_app

# Adaptar o app Flask para WSGI para Vercel
app = make_wsgi_app(user_app.app)
