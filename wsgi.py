import sys
import os

# Add your project directory to the Python path
path = '/home/YOUR_USERNAME/mgbric'
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app
from webhook_server import app as application

# WSGI application entry point
if __name__ == "__main__":
    application.run()
