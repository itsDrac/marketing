from app import db
from app.models import Client as ClientModel
from app.utils import current_agency, email_server_value
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, ReadOnly
import wtforms as wtf


class ClientForm(FlaskForm):
    name = wtf.StringField("Full name", validators=[DataRequired()])
    email = wtf.EmailField("Email", validators=[DataRequired()])
    phone = wtf.StringField("Phone number", validators=[DataRequired()])
    aircall_id = wtf.StringField("Aircall api ID")
    aircall_key = wtf.StringField("Aircall api Key")
    submit = wtf.SubmitField("Add Client")

    def validate_email(self, field):
        q = (
            db.select(ClientModel)
            .where(ClientModel.email == field.data.lower())
            .where(ClientModel.agency_id == current_agency.id)
        )
        existingClient = db.session.scalar(q)
        if existingClient:
            print("Client email ValidationError")
            raise ValidationError("Client with this email already exist")


class ClientUpdateForm(FlaskForm):
    name = wtf.StringField("Full name", validators=[ReadOnly()])
    email = wtf.EmailField("Email", validators=[ReadOnly()])
    email_password = wtf.StringField("Email Password")
    email_server = wtf.SelectField("Email Server", coerce=email_server_value)
    submit = wtf.SubmitField("Update Client")

    def pre_fill_details(self, name, email):
        self.name.data = name
        self.email.data = email


class ClientEditForm(FlaskForm):
    # TODO: Need to update validation for this class.
    name = wtf.StringField("Full name", validators=[DataRequired()])
    email = wtf.EmailField("Email", validators=[DataRequired()])
    phone = wtf.StringField("Phone number", validators=[DataRequired()])
    email_server = wtf.SelectField("Email Server", coerce=email_server_value)
    aircall_id = wtf.StringField("Aircall api ID")
    aircall_key = wtf.StringField("Aircall api Key")
    submit = wtf.SubmitField("Update Client")

    def __init__(self, originalemail, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.originalemail = originalemail

    def pre_fill_data(self, existingClient):
        self.name.data = existingClient.name
        self.email.data = existingClient.email
        self.phone.data = existingClient.phone
        self.email_server.data = existingClient.email_server
        self.aircall_id.data = existingClient.aircall_id
        self.aircall_key.data = existingClient.aircall_key

    def validate_email(self, field):
        if not self.originalemail == field.data.lower():
            q = (
                db.select(ClientModel)
                .where(ClientModel.email == field.data.lower())
                .where(ClientModel.agency_id == current_agency.id)
            )
            existingClient = db.session.scalar(q)
            if existingClient:
                raise ValidationError("Client with this email already exist")
