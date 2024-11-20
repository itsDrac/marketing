from flask import Blueprint


bp = Blueprint('client',
               __name__,
               template_folder="templates",
               )


from app.client import routes
