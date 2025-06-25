from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = 'i_dont_know_what_this_does_except_it_being_important_for_sessions'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'blog.db')

db = SQLAlchemy(app)
class Blogpost(db.Model):
    """Create a table in the database"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
with app.app_context():
    """initialize database"""
    db.create_all()

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = hashlib.sha256('somethingsecure'.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    """verify plain password against its hashed password"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login/', methods=['GET', 'POST'])
def login():
    """admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH):
            session['is_admin'] = True
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout/')
def logout():
    """admin logout"""
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    """shows all blog posts ordered by date_posted"""
    page = request.args.get('page', 1, type=int)
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).paginate(
        page=page,
        per_page=4
    )
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
@admin_required
def add():
    """opens HTML-form to create blog post"""
    return render_template('add.html')

@app.route('/addpost/', methods=['POST'])
@admin_required
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
@admin_required
def edit(post_id):
    """edit single blog post"""
    post = Blogpost.query.get_or_404(post_id)
    return render_template('edit.html', post=post)

@app.route('/updatepost/<int:post_id>/', methods=['POST'])
@admin_required
def updatepost(post_id):
    """commit to updating the post"""
    post = Blogpost.query.get_or_404(post_id)
    post.title = request.form['title']
    post.author = request.form['author']
    post.content = request.form['content']
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))

@app.route('/delete/<int:post_id>/')
@admin_required
def delete(post_id):
    """delete a single blog post"""
    post = Blogpost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=5551, debug=True )