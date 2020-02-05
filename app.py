"""  """

from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SECRET_KEY"] = "Shh! Don't tell!"

debug = DebugToolbarExtension(app)
