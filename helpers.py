from functools import wraps
from flask import redirect, render_template, request, session


def login_required(f):
    # http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function