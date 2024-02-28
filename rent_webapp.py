from flask import request
from app import app, db
from app.models import User, Car, Booking, Renewal, Contacts, Groups

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Car': Car, 'Booking': Booking, 
            'Renewal': Renewal, 'Contacts': Contacts, 'Groups': Groups}

# export FLASK_DEBUG=1