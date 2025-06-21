from flask import Flask, render_template, request, redirect, url_for
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
    """shows all blog posts ordered by date_posted"""
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/about/')
def about():
    """static HTML file with information about me"""
    return render_template('about.html')

@app.route('/post/<int:post_id>/')
def post(post_id):
    """shows a single blog post"""
    post = Blogpost.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/add/')
def add():
    """opens HTML-form to create blog post"""
    return render_template('add.html')

@app.route('/addpost/', methods=['POST'])
def addpost():
    """for posting a blog post to the database"""
    title = request.form['title']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, author=author, content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:post_id>/')
def edit(post_id):
    """edit single blog post"""
    post = Blogpost.query.get_or_404(post_id)
    return render_template('edit.html', post=post)

@app.route('/updatepost/<int:post_id>/', methods=['POST'])
def updatepost(post_id):
    """commit to updating the post"""
    post = Blogpost.query.get_or_404(post_id)
    post.title = request.form['title']
    post.author = request.form['author']
    post.content = request.form['content']
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))

@app.route('/delete/<int:post_id>/')
def delete(post_id):
    """delete a single blog post"""
    post = Blogpost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=5551, debug=True )