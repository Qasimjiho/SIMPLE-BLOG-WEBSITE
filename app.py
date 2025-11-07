import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
import sqlite3

db_path = db_path = os.path.join(os.path.dirname(__file__), 'blog.db')

db_dir = os.path.dirname(db_path)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Add this block after db_path and before Flask app initialization
def add_picture_column_if_missing(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(blogpost)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'picture' not in columns:
        cursor.execute("ALTER TABLE blogpost ADD COLUMN picture TEXT")
        conn.commit()
    conn.close()

add_picture_column_if_missing(db_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

try:
    db = SQLAlchemy(app)
except Exception as e:
    print(f"Database initialization error: {e}")
    raise

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    picture = db.Column(db.String(100))  # Add this line

# Create tables if they do not exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    return render_template('post.html', post=post)

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/delete')
def delete():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('delete.html', posts=posts)

@app.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']
    picture_file = request.files.get('picture')
    picture_filename = None
    if picture_file and picture_file.filename:
        upload_folder = os.path.join('static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        picture_filename = datetime.now().strftime('%Y%m%d%H%M%S_') + picture_file.filename
        picture_path = os.path.join(upload_folder, picture_filename)
        picture_file.save(picture_path)
    post = Blogpost(
        title=title,
        subtitle=subtitle,
        author=author,
        content=content,
        date_posted=datetime.now(),
        picture=picture_filename
    )
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/deletepost', methods=['DELETE','POST'])
def deletepost():
    post_id = request.form.get("post_id")

    post = Blogpost.query.filter_by(id=post_id).first()

    db.session.delete(post)
    db.session.commit()
    
    return redirect(url_for('index'))

if __name__ == '__main__':

    app.run(debug=True)

