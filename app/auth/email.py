from flask_mail import Message
from flask import current_app
from app import mail
from flask import render_template
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()


def send_password_reset_email(user):
    print("Sending Email Now")
    token = user.get_reset_password_token()
    send_email('[Poem] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
                                        
def send_message_to_admins(form):
    print("Sending Email to Admins")
    send_email(form.subject.data, sender=form.email.data, 
                    recipients=current_app.config['ADMINS'],
                    text_body = form.content.data,
                    html_body= f'<div style="border: 3px solid black; padding: 20px;"><h3>From: {form.name.data}</h3><hr><p>{form.content.data}</p></div>')
