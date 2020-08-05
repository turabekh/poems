from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import User, Poem, Category
from flask_login import current_user


class PoemForm(FlaskForm):
    category = SelectField("Category", coerce=int)
    title = StringField("Title", validators=[DataRequired()])
    body = TextAreaField('Enter Your Poem', validators=[
        DataRequired()])
    submit = SubmitField('Submit')

class CategoryForm(FlaskForm):
    name = StringField("Category", validators=[DataRequired()])
    submit = SubmitField('Submit')


    def validate_categoryname(self, username):
        category = Category.query.filter_by(name=name.data).first()
        if name is not None:
            raise ValidationError('Please use a different category name. It already exists.')
