from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import *
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user
from flask import request
from flask import Flask, request, render_template
import sqlite3

from sqlalchemy.testing.pickleable import User
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
app.app_context().push()
login_manager = LoginManager(app)


@app.route('/authorization', methods=['GET', 'POST'])
def form_authorization():
   if request.method == 'POST':
       Login = request.form.get('Login')
       Password = request.form.get('Password')

       db_lp = sqlite3.connect('login_password.db')
       cursor_db = db_lp.cursor()
       cursor_db.execute(('''SELECT password FROM passwords
                                               WHERE login = '{}';
                                               ''').format(Login))
       pas = cursor_db.fetchall()

       cursor_db.close()
       try:
           if pas[0][0] != Password:
               return render_template('auth_bad.html')
       except:
           return render_template('auth_bad.html')

       db_lp.close()
       return render_template('successfulauth.html')

   return render_template('authorization.html')

class Article(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Article %r>' % self.id

@app.route('/posts')
def posts():
    articles = Article.query.filter_by(completed=False).all()
    return render_template("posts.html", articles=articles)

@app.route('/completed_posts')
def completed_posts():
    articles = Article.query.filter_by(completed=True).all()
    return render_template("completed_tasks.html", articles=articles)

@app.route('/posts/<int:id>/check')
def mark_as_completed(id):
    task = Article.query.get_or_404(id)
    task.completed = True
    db.session.commit()
    return redirect('/posts')

@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)

@app.route('/posts/<int:id>/del')
def post_delete(id):
    article = Article.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "error"

@app.route('/completed_posts/<int:id>/del')
def completed_post_delete(id):
    article = Article.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/completed_posts')
    except:
        return "error"


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        article = Article(title=title, intro=intro, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "error"

    else:
        return render_template("create.html")

@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']
        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "error update"
    else:
        return render_template("post_update.html", article=article)


@app.route('/registration', methods=['GET', 'POST'])
def form_registration():

   if request.method == 'POST':
       Login = request.form.get('Login')
       Password = request.form.get('Password')

       db_lp = sqlite3.connect('login_password.db')
       cursor_db = db_lp.cursor()
       sql_insert = '''INSERT INTO passwords VALUES('{}','{}');'''.format(Login, Password)

       cursor_db.execute(sql_insert)
       db_lp.commit()

       cursor_db.close()
       db_lp.close()

       return render_template("successfulregis.html")

   return render_template("registration.html")

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

