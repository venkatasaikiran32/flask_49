from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
mongo = PyMongo(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email': request.form['email']})

        if existing_user is None:
            hashpass = request.form['password']
            users.insert_one({'email': request.form['email'], 'password': hashpass})
            user = User(request.form['email'])
            login_user(user)
            return redirect(url_for('welcome'))

        flash('Email already exists!')
        return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'email': request.form['email']})

        if login_user:
            if request.form['password'] == login_user['password']:
                user = User(login_user['email'])
                login_user(user)
                return redirect(url_for('welcome'))

        flash('Invalid email/password')
        return redirect(url_for('signin'))

    return render_template('signin.html')

@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html', email=current_user.id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))

if __name__ == "__main__":
    app.run(debug=True)
