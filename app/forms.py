from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, ValidationError

# Function to validate price is in the form __.xx
def check_price_format(form, field):
    # Check positive
    if field.data < 0:
        raise ValidationError("Price must be positive")
    
    # Check decimals
    if field.data: # If price inputted
        if '.' in str(field.data): # If contains decimal point
            decimals = str(field.data).split('.')[-1] # Right of decimal place
            if len(decimals) > 2:
                # Too many decimal places
                raise ValidationError("Invalid price format")
            
# GIFTS
class GiftForm(FlaskForm):
    # Name
    name = StringField('Gift Name', validators=[DataRequired(), Length(max=100)])
    # Price
    price = FloatField('Price', validators=[DataRequired(message="Must input a valid number"), check_price_format])
    # Link
    link = StringField('Link', validators=[Optional(), Length(max=200)])
    # Description
    description = TextAreaField('Description', validators=[Optional()])
    # Priority
    priority = SelectField(
        'Priority: 1 (Lowest) to 5 (Highest)', 
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], # Drop down, select 1-5
        coerce=int,
        validators=[DataRequired()]
    )
    # Submit
    submit = SubmitField('Save Gift')


# WISHLISTS
class WishListForm(FlaskForm):
    # Wish list name
    name = StringField('Wishlist Name', validators=[DataRequired(), Length(max=40)])
    # Submit
    submit = SubmitField('Save Wishlist')

# REGISTER
class RegisterForm(FlaskForm):  
    # Username
    username = StringField('Username', validators = [DataRequired(),Length(max=40)])
    # Password
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    # Password Confirmation
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # Submit 
    submit = SubmitField('Register')

# LOG IN
class LogInForm(FlaskForm):
    # Username
    username = StringField('Username', validators = [DataRequired(), Length(max=40)])
    # Password
    password = PasswordField('Password', validators=[DataRequired()])
    # Submit 
    submit = SubmitField('Login')

# CREATE FAMILY
class CreateFamilyForm(FlaskForm):
    # Family name
    name = StringField('Family Name', validators=[Length(max=40)])
    # Submit
    submit = SubmitField('Create Family')

# JOIN FAMILY
class JoinFamilyForm(FlaskForm):
    # Family join code - custom message for clarity
    join_code = StringField('Family Join Code', validators=[Length(min=8, max=8, 
                                                            message="Join code must be 8 characters")])
    # Submit
    submit = SubmitField('Join Family')


class AddCollaboratorForm(FlaskForm):
    # Collaborator
    collaborator = SelectField('Add Collaborator', coerce=int, validators=[DataRequired()])
    # Submit
    submit = SubmitField('Add Collaborator')