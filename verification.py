from functools import wraps
from flask import g, request, redirect, url_for, flash


def verify_user(f):
    @wraps(f)
    def wraped(*args, **kwargs):
        
        if g.user is None:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        return f(*args, **kwargs)
    return wrapped
        



 @app.route('address')
 @verify
 def func:


func = route('address')(func)   

