from flask import Blueprint, render_template


bp = Blueprint('main', __name__)


@bp.route("/")
@bp.route("/home")
def home():
    return render_template("home.html", title="Home Page")
