from flask import render_template, redirect, session, request, flash
from flask_app import app
from flask_app.models.user import User
from flask_app.models.post import Post
from flask_app.models.like import Like
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    if not User.validate_register(request.form):
        return redirect('/')
    data = {
        'firstName' : request.form['firstName'],
        'lastName' : request.form['lastName'],
        'email' : request.form['email'],
        'password' : bcrypt.generate_password_hash(request.form['password'])
    }
    id = User.save(data)
    session['user_id'] = id
    return redirect('/dashboard')

@app.route('/login', methods=['POST'])
def login():
    user = User.get_by_email(request.form)
    if not user:
        flash('Invalid Login', 'login')
        return redirect('/')
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash('Invalid Login', 'login')
        return redirect('/')
    session['user_id'] = user.id
    return redirect('/dashboard')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    if request.method == 'POST':
        if request.form.get('like_post_id'):
            data = {
                'post_id' : request.form['like_post_id'],
                'user_id' : session['user_id']
            }
            Like.save(data)
        else:
            if not Post.validate_post(request.form):
                return redirect('/dashboard')
            data = {
                'content' : request.form['content'],
                'user_id' : session['user_id']
            }
            Post.save(data)
    userData ={
        'id': session['user_id']
    }
    user = User.get_by_id(userData)
    posts = Post.get_all_posts()
    for post in posts:
        post.user = User.get_by_id({'id':post.user_id})
        post.likes = Like.count_likes({'post_id' : post.id})
    return render_template('dashboard.html', user=user, posts=posts)

@app.route('/profile/<id>')
def profile(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data ={
        "id": session['user_id']
    }
    user = User.get_by_id({'id': id})
    return render_template('profile.html', user=user, all_posts=User.get_all_users_posts(data))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')