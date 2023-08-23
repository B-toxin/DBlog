import time

from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from FlaskBlog import db, bcrypt
from FlaskBlog.models import User, Post
from FlaskBlog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm, PaymentForm)
from FlaskBlog.users.utils import save_picture, send_reset_email
from werkzeug.urls import url_parse
import requests
from FlaskBlog.config import Config

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            return redirect(url_for('users.login'))  # Redirect to login page on failed login

    return render_template('login.html', title='Login', form=form)


@users.route('/Login/<int:post_id>', methods=['GET', 'POST'])
def Login(post_id):
    if current_user.is_authenticated:
        return redirect(url_for('posts.post', post_id=post_id))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.home')

            return redirect(next_page)  # Redirect to intended page after successful login

        flash('Login Unsuccessful. Please check email and password', 'danger')

    flash('You must log in first', 'info')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=3)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@users.route("/payments", methods=['GET', 'POST'])
def payments():
    form = PaymentForm()

    if form.validate_on_submit():
        amount_in_kobo = int(form.amount.data * 100)  # Convert NGN to kobo
        paystack_data = {
            'key': 'pk_test_60a3e1f9abc3bbe710308289a796d2e7b6f428ad',
            'email': form.email.data,
            'amount': amount_in_kobo,
            'currency': 'NGN',
            'ref': f'paystack_example_{int(time.time())}',
            # Add other Paystack parameters as needed
        }

        # Make the payment using Paystack API
        response = requests.post('https://api.paystack.co/transaction/initialize', json=paystack_data)
        payment_data = response.json()

        if payment_data.get('status') and payment_data.get('data').get('status') == 'success':
            # Payment initiation successful, redirect to Paystack payment page
            return redirect(payment_data.get('data').get('authorization_url'))

        # Payment initiation failed, handle the error accordingly

    return render_template('payments.html', form=form)


@users.route('/payment/callback', methods=['POST'])
def payment_callback():
    event = request.json
    payment_reference = event['data']['reference']
    verify_url = f'https://api.paystack.co/transaction/verify/{payment_reference}'
    headers = {
        'Authorization': f'Bearer {Config.PAYSTACK_SECRET_KEY}'
    }
    response = requests.get(verify_url, headers=headers)
    data = response.json()

    if data['status'] and data['data']['status'] == 'success':
        # Payment was successful, verify the payment details
        amount_paid = data['data']['amount'] / 100  # Convert amount from kobo to NGN
        email = data['data']['customer']['email']

        # You can update your database or perform other actions here
        return jsonify({'message': 'Payment verified and successful'})
    else:
        # Payment was not successful, handle accordingly
        return jsonify({'message': 'Payment verification failed'})
