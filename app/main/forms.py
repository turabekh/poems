from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email



class ContactUsForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField('Subject')
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    parent_id = HiddenField()
    body = StringField('Content', validators=[DataRequired()])
