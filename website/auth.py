from flask import Blueprint,render_template,request,flash,redirect,url_for
from .models import User
from . import db
from flask_login import login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash

auth = Blueprint('auth',__name__)


@auth.route('/login', methods=["GET", "POST"])
def login():
   if current_user.is_authenticated:
        return redirect(url_for('views.home'))
   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        remember = request.form.get('remember')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.username != username:
                flash('Incorrect Username', category='error')
            elif check_password_hash(user.password, password):
                flash(f'Welcome, {user.username}', category='success')
                if remember:
                  login_user(user,remember=True)
                else:
                   login_user(user,remember=False)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password', category='error')
        else:
            flash('No account found with that email', category='error')

   return render_template('login.html')
 

@auth.route('/signup',methods=["GET","POST"])
def signup():
   if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       confirm_password = request.form['confirm_password']
       email = request.form['email']
       
       user = User.query.filter_by(email=email).first()

       if user:
          flash('Email already exists',category='error')
       if len(email) < 4:
          flash("Email must be greater than 4 characters",category="error")
       elif len(username) < 3:
          flash("Username must be greater than or equal to 3 characters",category="error")
       elif password != confirm_password:
          flash("Passwords don't match",category="error")
       elif len(password) <= 8:
          flash("Password must be of 8 characters",category="error")
       else:
          new_user = User(email=email,username=username,password=generate_password_hash(password,method='pbkdf2:sha256'))
          db.session.add(new_user)
          db.session.commit()
          flash('Account created!',category="success")
          return redirect(url_for('auth.login'))
   return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('views.start'))