from app import db
from datetime import datetime
from flask import (
    render_template, 
    flash, 
    redirect, 
    url_for,
    request
)
from app.auth.forms import (
    LoginForm, 
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm
)

from app.main.models import User
from flask_login import (
    current_user, 
    login_user, 
    logout_user,
    login_required
)
from werkzeug.urls import url_parse
from app.auth.email import send_mail, send_password_reset_email
from app.auth import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid user login credentials!')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data.lower(),
        )

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! Yay!')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/register.html', 
        title='Register', 
        form=form
    )

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        url = ''
        if user:
            url = send_password_reset_email(user)
        flash(url)
        # flash('Password reset instructions have been sent to your email')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
        title='reset Password', form=form)

@bp.route('/reset_password/<string:token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset!')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
