from flask import Blueprint


bp = Blueprint('agency',
               __name__,
               template_folder="templates",
               )


from app.agency import routes
