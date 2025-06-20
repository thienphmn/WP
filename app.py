from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'blog.db')

db = SQLAlchemy(app)

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

# delete this after finalizing the model
with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return render_template("index.html")
@app.route('/about')
def confirm():
    return "Your redirect worked!"

if __name__ == '__main__':
    app.run(port=5551, debug=True )