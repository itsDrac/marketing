from flask import Blueprint


bp = Blueprint('lead',
               __name__,
               template_folder="templates",
               )


from app.lead import routes
