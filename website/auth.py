from flask import Blueprint,render_template,flash, url_for, redirect
from flask.globals import request
import re
from .model import Users
from flask_login import login_user,login_required,logout_user, current_user
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        mail=request.form.get('email')
        pword = request.form.get('password')
        exp ="^(?:\d{11}|\w+@\w+\.\w{2,3})$"
        
        if re.search(exp, mail):
            if mail.startswith('0'):
                mail = mail.replace("0", "+234",1)
            user = Users.query.filter_by(email=mail, isDeleted = 0).first()
            phoneChk = Users.query.filter_by(phone_number=mail, isDeleted = 0).first()
            if user:
                if check_password_hash(user.password,pword):
                    login_user(user, remember=True)
                    return redirect(url_for("admin.admin_home"))
                else:
                    flash('Incorrect email or password', category='error')
            elif phoneChk:
                if check_password_hash(phoneChk.password,pword):
                    login_user(user, remember=True)
                    return redirect(url_for("admin.admin_home"))
                
            else:
                flash('Incorrect email or password', category='error')
    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/reset_password')
def reset_password():
    pass

@auth.route('register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        phone = request.form.get('tel')
        pword = request.form.get('passw')
        cpassW = request.form.get('cPassw')

        fields = [email,first_name,last_name,phone,pword,cpassW]
        reg = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$' #regex for email
        phone_reg ='^\+[1-9]{1}[0-9]{3,14}$' #regex for phone numer
        for field in fields:
            if len(field) == 0:
                flash('All fields are required', category='error')
        
        if pword != cpassW:
            flash("Passwords and confirm password do not match", category='error')
        elif not re.search(reg, email):
            flash('mail is incorrect', category='error')
        elif len(pword) <6:
            flash("Password must be at least 6 characters", category='error')
        elif len(first_name) < 3:
            flash("First name must be more than 3 characters", category='error')
        elif len(last_name) < 3:
            flash("last name must be more than 3 characters", category='error')
        elif not re.search(phone_reg,phone):
            flash("start phone number with +234 not 0 eg. +2348057125573", category='error')
        else:
            user = Users.query.filter_by(email=email).first()
            if user:
                flash('Email already exists', category='error')
            else:
                new_user = Users(email=email, first_name=first_name,last_name=last_name, password=generate_password_hash(pword, method="sha256"), phone_number=phone, role=0, isDeleted = 0)
                db.session.add(new_user)
                db.session.commit()
                flash('Account created, login in now', category='success')
                return redirect(url_for("auth.login"))
        
    return render_template("register.html")