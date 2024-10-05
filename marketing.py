if __name__ == "__main__":
    print("This is main file")

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"sa": sa, "so": so, "db": db}
