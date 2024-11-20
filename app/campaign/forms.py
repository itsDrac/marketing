from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Optional
import wtforms as wtf


class CampaignForm(FlaskForm):
    name = wtf.StringField("Name", validators=[DataRequired()])
    start_date = wtf.DateField("Start Date", validators=[DataRequired()])
    end_date = wtf.DateField("End Date", validators=[Optional()])
    submit = wtf.SubmitField("Add Campaign")

    def validate_end_date(self, field):
        print(field.data)
        if field.data:
            if self.start_date.data > field.data:
                print("Raise validation error")
                raise ValidationError("Client with this email already exist")
