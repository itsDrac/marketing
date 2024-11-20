import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import Agency, Client, Campaign, Lead
from dotenv import load_dotenv


load_dotenv()
app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
       "sa": sa, "so": so, "db": db,
       "A": Agency, "C": Client, "Cam": Campaign, "L": Lead
    }


if __name__ == "__main__":
    app.run()
