from flask_mail import Message
from app import mail
from flask import (
    render_template, 
    url_for,
    current_app
)
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(**kwargs):

    subject = kwargs.get('subject')
    sender = kwargs.get('sender')
    recipients = kwargs.get('recipients')
    text_body = kwargs.get('text_body')
    html_body = kwargs.get('html_body')

    message = Message(
        subject,
        sender=sender,
        recipients=recipients
    )

    message.body = text_body
    message.html = html_body

    Thread(
        target=send_async_email, 
        args=(current_app._get_current_object(), message)
    ).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail(
        subject='Flask Course: Reset your password!',
        sender=current_app.config['MAIL_SENDER'],
        recipients=[user.email],
        text_body=render_template(
            'email/reset_password.txt',
            user=user, 
            token=token
        ),
        html_body=render_template(
            'email/reset_password.html',
            user=user, 
            token=token
        )
    )
    return url_for('reset_password', token=token, _external=True)