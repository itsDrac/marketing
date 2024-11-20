from app import db
from app.models import Agency as AgencyModel
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Length, EqualTo
import wtforms as wtf


class LoginForm(FlaskForm):
    email = wtf.EmailField("Email", validators=[DataRequired()])
    password = wtf.PasswordField("Password", validators=[DataRequired(), Length(min=2)])
    remember = wtf.BooleanField("Remember me?", default=True)
    submit = wtf.SubmitField("Login")

    def validate_email(self, field):
        q = db.select(AgencyModel).where(AgencyModel.email == field.data.lower())
        existingAgency = db.session.scalar(q)

        if not existingAgency:
            raise ValidationError("No Account with this email")


class RegisterForm(FlaskForm):
    name = wtf.StringField("Full name", validators=[DataRequired()])
    email = wtf.EmailField("Email", validators=[DataRequired()])
    password = wtf.PasswordField("Password", validators=[
        DataRequired(),
        Length(min=2),
        EqualTo("confirm", message="Password should match.")
    ])
    confirm = wtf.PasswordField("Repeat password")
    submit = wtf.SubmitField("Register")

    def validate_email(self, field):
        q = db.select(AgencyModel).where(AgencyModel.email == field.data.lower())
        existingAgency = db.session.scalar(q)

        if existingAgency:
            raise ValidationError("Account with this email already exist, Please login.")
