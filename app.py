from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Email, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Review

app = Flask(__name__)
app.secret_key = 'reviewsecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ---------- Forms ----------
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class ReviewForm(FlaskForm):
    movie = StringField("Movie Title", validators=[InputRequired()])
    rating = IntegerField("Rating (1-10)", validators=[InputRequired(), NumberRange(min=1, max=10)])
    comment = TextAreaField("Comment", validators=[InputRequired()])
    submit = SubmitField("Submit Review")

# ---------- Routes ----------
# @app.before_first_request
# def create_tables():
#     db.create_all()

@app.route('/')
def home():
    reviews = Review.query.all()
    return render_template('home.html', reviews=reviews)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Logged in successfully!", "info")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out!", "info")
    return redirect(url_for('login'))

@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    if 'user_id' not in session:
        flash("Login required to submit a review!", "warning")
        return redirect(url_for('login'))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            movie=form.movie.data,
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=session['user_id'],
            username=session['username']
        )
        db.session.add(review)
        db.session.commit()
        flash("Review submitted!", "success")
        return redirect(url_for('home'))
    return render_template('add_review.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)