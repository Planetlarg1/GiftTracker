from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash # For password hasing
from .models import User, Family
from app import db
from .forms import RegisterForm, LogInForm, CreateFamilyForm, JoinFamilyForm
import random, string # For join code generation

# Authentication Blueprint
auth_bp = Blueprint('auth', __name__)

# USER REGISTRATION ROUTE
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    create_form = CreateFamilyForm()
    join_form = JoinFamilyForm()

    if form.validate_on_submit():
        # Check if username exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            # Username unavailable
            flash("Account creation failed - username unavailable", "danger")
            return redirect(url_for('auth.login'))

        # Hash password and create user
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)

        # CREATE FAMILY
        if 'create_family' in request.form:
            if create_form.validate_on_submit():
                family_name=create_form.name.data
                if len(family_name) < 1:
                    flash("Account creation failed - Must create or join a family", "danger")
                    return redirect(url_for('auth.login'))
                # Generate random unique 8-character alphanumerical code
                # E.g. HD93NG93
                unique_code = False
                while not unique_code:
                    join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not Family.query.filter_by(join_code=join_code).first():
                        unique_code = True

                # Add family to DB
                new_family = Family(name=family_name, join_code=join_code)
                db.session.add(new_family)
                db.session.commit()
                # Link user to family
                new_user.family_id = new_family.id

        # JOIN FAMILY
        elif 'join_family' in request.form:
            if join_form.validate_on_submit():
                join_code = join_form.join_code.data
                family = Family.query.filter_by(join_code=join_code).first()

                # Invalid join code
                if not family:
                    flash("Account creation failed - invalid join code", "danger")
                    return redirect(url_for('auth.login'))

                # Link user to family
                new_user.family_id = family.id

        # Submit without joining/creating family
        else:
            flash("Account creation failed - Must create or join a family", "danger")
            return redirect(url_for('auth.login'))

        # Add user to DB and log in
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        # Successful registration - redirect to dashboard
        return redirect(url_for('wishlist.dashboard'))
    
    return render_template('register.html', form=form, create_form=create_form, join_form=join_form)

# USER LOGIN ROUTE
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        # Validate user credentials
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # Login user - Redirect to dashboard
            login_user(user)
            flash(f"{user.username} successfully logged in", 'success')
            return redirect(url_for('wishlist.dashboard'))
        # Invalid credentials
        flash("Invalid username or password", "danger")

    return render_template('login.html', form=form)

# LOG OUT ROUTE
@auth_bp.route('/logout')
@login_required # Must be logged in
def logout():
    logout_user()
    # Logout
    flash("You have been logged out", "info")
    return redirect(url_for('auth.login'))