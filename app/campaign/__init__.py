from flask import Blueprint


bp = Blueprint('campaign',
               __name__,
               template_folder="templates",
               )


from app.campaign import routes
