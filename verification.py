from functools import wraps
from flask import g, request, redirect, url_for, flash


def verify_user(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        
        if g.user is None:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        return f(*args, **kwargs)
    return wrapped


