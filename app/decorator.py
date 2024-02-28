from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def requires_verification(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to log in to access this page.', 'warning')
            return redirect(url_for('login'))  # Redirect to login page
        elif not current_user.is_verified:
            flash('You need to verify your account to access this page.', 'warning')
            return redirect(url_for('confirm_email'))  # Redirect to account verification page
        return func(*args, **kwargs)
    return decorated_function
