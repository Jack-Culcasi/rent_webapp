from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User, Car
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
import json


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('index')) 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST']) 
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@app.route('/garage_view', methods=['GET', 'POST'])
@login_required
def garage_view():
    user_cars = current_user.garage.all()
    return render_template('garage_view.html', title='Garage', page="garage_view", user_cars=user_cars)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/garage_manage', methods=['GET', 'POST'])
@login_required
def garage_manage():
    if request.method == 'POST':
        # Process the form data for a POST request
        plate = request.form.get('Plate').upper()
        make = request.form.get('Make').lower().capitalize()
        model = request.form.get('Model').lower().capitalize()
        fuel = request.form.get('Fuel').lower().capitalize()
        year = request.form.get('Year').lower().capitalize()
        cc = request.form.get('Cc').lower().capitalize()

        new_car = Car(plate=plate, make=make, model=model, fuel=fuel, year=year, cc=cc, user_id=current_user.id)

        db.session.add(new_car)
        db.session.commit()
        flash('Car added successfully', 'success')
        return redirect(url_for('garage_manage'))
    else:
        # Render the form for a GET request
        return render_template('garage_manage.html', title='Add Car', page="garage_manage")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Standardize the search input
        search_query = request.form.get('search_query')
        search_type = request.form.get('search_type')

        # Handle the "plate" field separately to keep it all uppercase
        if search_type == 'plate':
            search_query = search_query.upper()
        
        # Convert other fields to lowercase and capitalize the first letter
        else:
            search_query = search_query.lower().capitalize()

        # Perform the search and filter the cars based on the query and type
        if search_type == 'plate':
            filtered_cars = Car.query.filter_by(plate=search_query).all()
        elif search_type == 'make':
            filtered_cars = Car.query.filter_by(make=search_query).all()
        elif search_type == 'model':
            filtered_cars = Car.query.filter_by(model=search_query).all()
        elif search_type == 'fuel':
            filtered_cars = Car.query.filter_by(fuel=search_query).all()
        elif search_type == 'year':
            filtered_cars = Car.query.filter_by(year=search_query).all()
        elif search_type == 'cc':
            filtered_cars = Car.query.filter_by(cc=search_query).all()
        else:
            filtered_cars = []

        return render_template('garage_manage.html', cars=filtered_cars, search_type=search_type, search_query=search_query)
    else:
        # Render the search page template for a GET request
        return render_template('garage_manage.html')

@app.route('/delete', methods=['POST'])
def delete_car():
    car_plate = request.form.get('car_plate')
    if car_plate:
        car = Car.query.filter_by(plate=car_plate).first()
        if car:
            db.session.delete(car)
            db.session.commit()
            flash('Car deleted successfully.', 'success')
        else:
            flash('Car not found.', 'error')
    else:
        flash('Invalid request.', 'error')
    return redirect(url_for('search'))