import re
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from celery import Celery
from flask_mail import Mail, Message
from flask import Flask, flash, request, render_template, jsonify, session, redirect, url_for


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ('FLASK_SECRET')
# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ['MAIL_DEFAULT_SENDER']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = os.environ['MAIL_DEFAULT_SENDER']

# Celery configuration
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
app.config['CELERY_RESULT_BACKEND'] = os.environ['CELERY_BROKER_URL']

# Initialize extensions
mail = Mail(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Create Celery Email task worker
@celery.task
def send_async_email(args):
    """Background task to send an email with Flask-Mail."""
    with app.app_context():
        for email in args['to']:
            if not valid_email_address(email):
                app.logger.warn("Invalid Email Address" + str(email))
        msg = Message(args['subject'],
                  recipients=args['to'])
        for content in args['content']:
            if content['type'] == "text/plain":
                msg.body = content['value']
            else:
                msg.html = content['value']
        mail.send(msg)


# https://github.com/lgp171188/flask-form-validation/blob/master/app.py
def valid_email_address(email):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
        return False
    return True


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email
    params = {"to": [email], "subject": "Send from UI", "content": [{"type": "text/plain", "value": "Hello World :) !"}]}
    if request.form['submit'] == 'Send':
        # send right away
        send_async_email.delay(params)
        flash('Sending email: {0}'.format(email))

    return redirect(url_for('index'))

@app.route('/v1/mail/send', methods=['POST'])
def send():
    if request.headers['Content-Type'] == 'application/json':
        args = request.get_json()
        if 'to' not in args or len(args['to']) not in range(0, 501):
            return jsonify({"message": "Invalid to field", "status": 400})
        if 'content' not in args or len(args['content']) == 0:
            return jsonify({"message": "Invalid content field", "status": 400})
        send_async_email.delay(args)
        return jsonify({"message": "Successfully Queued", "status": 200})
    else:
        return jsonify({"message": "Unsupported Media Type ;)", "status": 415})

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
    app.run(debug=True)