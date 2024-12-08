import os

# Flask Configuration
SECRET_KEY = 'your_secret_key_here'

# Flask-Mail Configuration
MAIL_SERVER = 'smtp.gmail.com'  # Gmail's SMTP server
MAIL_PORT = 587                 # Use 587 for TLS
MAIL_USE_TLS = True             # Enable TLS encryption
MAIL_USE_SSL = False            # SSL is not used here
MAIL_USERNAME = 'dotunomoboye@gmail.com'  # Your Gmail address
MAIL_PASSWORD = '09070000'                # Your Gmail password or App Password

MAIL_DEBUG = True
