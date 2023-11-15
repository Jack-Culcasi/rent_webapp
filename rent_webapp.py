from flask import request
from app import app, db
from app.models import User, Car

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Car': Car}

# export FLASK_DEBUG=1