
import flask
import flask_sqlalchemy
import time

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use Azure SQL connection string in production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def home():
    return render_template('index.html', datetime=datetime.now())

@app.route('/about')
def about():
    return render_template('about.html' , datetime=datetime.now())

@app.route('/topics')
def topics():
    topics_list = ["Health", "Education", "Technology"]
    return render_template('topics.html', topics=topics_list, datetime=datetime.now())

@app.route('/topic/<string:name>')
def topic_detail(name):
    subtopics = {
        "Health": ["Nutrition", "Mental Health"],
        "Education": ["E-learning", "Higher Education"],
        "Technology": ["AI", "Cybersecurity"]
    }
    return render_template('topic_detail.html', topic=name, subtopics=subtopics.get(name, []),
                           datetime=datetime.now())


@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        username = request.form.get('username')
        content = request.form.get('content')
        if username and content:
            new_comment = Comment(username=username, content=content)
            db.session.add(new_comment)
            db.session.commit()
        return redirect(url_for('comments'))
    all_comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    return render_template('comments.html', comments=all_comments,datetime=datetime.now())

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # 1. Save to DB
        contact_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(contact_message)
        db.session.commit()

        # 2. Send Email
        msg = Message(
            subject=f"New Contact Form Submission from {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=['your_email@gmail.com'],  # You can add more here
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        )
        mail.send(msg)

        return redirect(url_for('home'))

    return render_template('contact.html')

@app.context_processor
def inject_datetime():
    from datetime import datetime
    return {'datetime': datetime}


class ContactMessage(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(120), nullable=False)
  message = db.Column(db.Text, nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.now)


# this will send email

from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'  # Use an App Password, not your real password

mail = Mail(app)


with app.app_context():
  db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
