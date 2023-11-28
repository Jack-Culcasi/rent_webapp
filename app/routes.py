#Flask imports
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime, timedelta

# Local imports
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Car, Booking

                                                                                # Users Login/Logout

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('overview')) 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('overview')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST']) 
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('overview'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('overview'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('overview'))

                                                                                # Garage

@app.route('/garage_view', methods=['GET', 'POST'])
@login_required
def garage_view():
    user_cars = current_user.garage.all()
    return render_template('garage_view.html', title='Garage', page="garage_view", user_cars=user_cars)

@app.route('/garage_manage', methods=['GET', 'POST'])
@login_required
def garage_manage(): # Add Car
   if request.method == 'POST':
       # Process the form data for a POST request
       plate = request.form.get('Plate').upper()
       make = request.form.get('Make').lower().capitalize()
       model = request.form.get('Model').lower().capitalize()
       fuel = request.form.get('Fuel').lower().capitalize()
       year = request.form.get('Year').lower().capitalize()
       cc = request.form.get('Cc').lower().capitalize()

       # Check if a car with the same plate and user_id already exists
       existing_car = Car.query.filter_by(plate=plate, user_id=current_user.id).first()
       if existing_car is not None:
           flash('A car with this plate already exists for this user', 'error')
           return redirect(url_for('garage_manage'))

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
        search_query = request.form.get('search_query')
        search_type = request.form.get('search_type')

        filtered_cars = Car.search(search_query, search_type, current_user.id)

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
            
            # Remove bookings associated with the car
            bookings_to_remove = Booking.query.filter_by(car_plate=car_plate).all()
            for booking in bookings_to_remove:
                Booking.remove_booking(booking.id)

            # Delete the car
            db.session.delete(car)
            db.session.commit()
            flash('Car deleted successfully.', 'success')
        else:
            flash('Car not found.', 'error')
    else:
        flash('Invalid request.', 'error')
    return redirect(url_for('search'))

@app.route('/')
@app.route('/overview', methods=['GET', 'POST'])
@login_required
def overview(): # Booking
    if request.method == 'POST':
        try:
            if 'book' in request.form:
                car_plate = request.form.get('car_selection')
                start_date = request.form.get('start_date')
                end_date = request.form.get('end_date')
                start_time = request.form.get('start_time')
                end_time = request.form.get('end_time')
                note = request.form.get('note')                

                # Convert start, end, to and from date and time to a datetime object
                start_datetime = datetime.strptime(f'{start_date} {start_time}', '%Y-%m-%d %H:%M')
                end_datetime = datetime.strptime(f'{end_date} {end_time}', '%Y-%m-%d %H:%M')

                # Check if start_datetime is in the past
                if start_datetime < datetime.now():
                    flash('Booking cannot be made for a past date and time.', 'error')
                    return redirect(url_for('overview'))                

                # Call the create_booking method from the Booking model
                booking, overlap_start, overlap_end = Booking.create_booking(
                    car_plate, start_datetime, end_datetime, current_user.id, note
                )
                
                if booking is None:
                    flash(f'This car is already booked from {overlap_start.strftime("%b %d %H:%M")} to {overlap_end.strftime("%b %d %H:%M")}!', 'error')
                else:
                    flash('Car booked successfully!', 'success')
                return redirect(url_for('overview'))  # Redirect after a successful form submission

            elif 'check' in request.form:
                # To check available and booked cars
                from_date = request.form.get('from')
                to_date = request.form.get('to')
                

        except ValueError as e:
            flash(str(e), 'error')
            print(f'ValueError: {str(e)}')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            print(f'Error: {str(e)}')

    user_cars = current_user.garage.all()

    # To check available and booked cars
    from_date = request.form.get('from')
    to_date = request.form.get('to')

    # Standard time frame if no Input
    if from_date == None:
        from_date = datetime.now().strftime('%Y-%m-%d')
        to_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    from_datetime = datetime.strptime(f'{from_date}', '%Y-%m-%d')
    to_datetime = datetime.strptime(f'{to_date}', '%Y-%m-%d')

    # Fetch all bookings for the user within the specified time range
    user_bookings = Booking.query.filter(
                Booking.user_id == current_user.id,
                Booking.end_datetime > from_datetime,
                Booking.start_datetime < to_datetime,
                Booking.end_datetime > datetime.now()  # Additional condition to exclude expired bookings
                ).all()

    # Extract the plates of booked cars
    booked_car_plates = [booking.car_plate for booking in user_bookings]

    # Filter out booked cars from available cars
    available_cars = [car for car in user_cars if car.plate not in booked_car_plates]

    # Check and deletes bookings older than 3 months
    three_months_ago = datetime.now() - timedelta(days=3 * 30)
    old_bookings = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (Booking.end_datetime < three_months_ago)
    ).all()
    
    # Delete the old booking
    for old_booking in old_bookings:
        Booking.remove_booking(old_booking.id)

    return render_template('overview.html',
                            user_cars=user_cars,
                            available_cars=available_cars,
                            user_bookings=user_bookings,
                            from_datetime=from_datetime.strftime('%Y-%m-%d'),
                            to_datetime=to_datetime.strftime('%Y-%m-%d'),
                            user_name=current_user.username if current_user.is_authenticated else None)

@app.route('/garage_car', methods=['GET', 'POST'])
@login_required
def garage_car():
    user_cars = current_user.garage.all()
    if request.method == 'POST':
        try:
            if 'plate' in request.form:
                car_plate = request.form.get('plate')
                car = Car.query.filter_by(plate=car_plate).first()
                return render_template('garage_car.html', title='Car', page="garage_car", user_cars=user_cars, car_object=car)
            
            elif request.form.get('action') == 'amend':
                car_plate = request.form['car_plate']
                selected_car = Car.query.filter_by(plate=car_plate).first()
                if selected_car:
                    try:
                        # Extracting form data
                        car_make = request.form['car_make']
                        car_model = request.form['car_model']
                        car_fuel = request.form['car_fuel']
                        car_year = request.form['car_year']
                        car_cc = request.form['car_cc']

                        # Call the amend_car method
                        selected_car.amend_car(car_plate, car_make, car_model, car_fuel, car_year, car_cc)

                        flash('Car amended successfully!', 'success')

                    except ValueError as e:
                        flash(str(e), 'error')  # Handle any parsing errors
                    except Exception as e:
                        flash(f'Error: {str(e)}', 'error')  # Handle other exceptions

            elif request.form.get('action') == 'delete':
                car_plate = request.form['car_plate']
                selected_car = Car.query.filter_by(plate=car_plate).first()
                if selected_car:
                    try:
                        # Remove bookings associated with the car
                        bookings_to_remove = Booking.query.filter_by(car_plate=car_plate).all()
                        for booking in bookings_to_remove:
                            Booking.remove_booking(booking.id)

                        # Delete the car
                        db.session.delete(selected_car)
                        db.session.commit()
                        flash('Car deleted successfully.', 'success')

                    except ValueError as e:
                        flash(str(e), 'error')  # Handle any parsing errors
                    except Exception as e:
                        flash(f'Error: {str(e)}', 'error')  # Handle other exceptions

            # Handles the "Manage" buttons in other pages
            elif request.form.get('garage_car'):
                car_plate = request.form.get('garage_car')
                selected_car = Car.query.filter_by(plate=car_plate).first()
                return render_template('garage_car.html', title='Car', page="garage_car", user_cars=user_cars, car_object=selected_car)
                
        except ValueError as e:
            flash(str(e), 'error')
            print(f'ValueError: {str(e)}')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            print(f'Error: {str(e)}')

    return render_template('garage_car.html', title='Car', page="garage_car", user_cars=user_cars)

                                                                                # Bookings 


@app.route('/bookings_view', methods=['GET', 'POST'])
@login_required
def bookings_view(): 
    current_date = datetime.utcnow()
    
    # Retrieve active bookings
    active_bookings = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (Booking.end_datetime > current_date)
    ).all()

    return render_template('bookings_view.html', user_bookings=active_bookings, page='bookings_view')

@app.route('/bookings_manage', methods=['GET', 'POST'])
@login_required
def bookings_manage():
    current_date = datetime.utcnow()
    
    # Retrieve active bookings
    user_bookings = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (Booking.end_datetime > current_date)
    ).all()
    selected_booking = None

    if request.method == 'POST':
        booking_id = request.form.get('search_type')
        selected_booking = Booking.query.filter_by(id=booking_id).first()

        if request.form.get('action') == 'delete':
            booking_id = request.form.get('booking_id')
            # Modify the query to eagerly load the 'car' relationship
            selected_booking = Booking.query.options(db.joinedload(Booking.car)).filter_by(id=booking_id).first()
            if selected_booking:
                Booking.remove_booking(booking_id)
                flash('Booking successfully deleted!', 'success')

                # Redirect to the same page to refresh
                return redirect(url_for('bookings_manage'))

        # Handles the "Manage" buttons in other pages
        if request.form.get('manage_booking'):
            booking_id = request.form.get('manage_booking')
            selected_booking = Booking.query.filter_by(id=booking_id).first()            

        # Check if the form was submitted for amendment
        if request.form.get('action') == 'amend':
            booking_id = request.form['booking_id']
            selected_booking = Booking.query.filter_by(id=booking_id).first()
            # Handle the amendment logic here, e.g., update the database
            if selected_booking:
                try:
                    # Extracting form data
                    start_date = request.form['start_date']
                    start_time = request.form['start_time']
                    end_date = request.form['end_date']
                    end_time = request.form['end_time']
                    note = request.form['note']

                    # Parsing form data to create datetime objects
                    start_datetime = datetime.strptime(f'{start_date} {start_time}', '%Y-%m-%d %H:%M')
                    end_datetime = datetime.strptime(f'{end_date} {end_time}', '%Y-%m-%d %H:%M')

                    # Call the amend_booking method
                    selected_booking.amend_booking(start_datetime, end_datetime, note)

                    flash('Booking amended successfully!', 'success')

                except ValueError as e:
                    flash(str(e), 'error')  # Handle any parsing errors
                except Exception as e:
                    flash(f'Error: {str(e)}', 'error')  # Handle other exceptions

            else:
                flash('Booking not found. Amendment failed.', 'error')

    return render_template('bookings_manage.html', page='bookings_manage', user_bookings=user_bookings, selected_booking=selected_booking)

@app.route('/bookings_history', methods=['GET', 'POST'])
@login_required
def bookings_history(): 
    current_date = datetime.utcnow()
    
    # Retrieve expired bookings
    expired_bookings = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (Booking.end_datetime < current_date)
    ).all()

    if request.method == 'POST':
        if request.form.get('delete'):
            booking_id = request.form.get('delete')
            # Modify the query to eagerly load the 'car' relationship
            selected_booking = Booking.query.options(db.joinedload(Booking.car)).filter_by(id=booking_id).first()
            if selected_booking:
                Booking.remove_booking(booking_id)
                flash('Booking successfully deleted!', 'success')

                # Redirect to the same page to refresh
                return redirect(url_for('bookings_history'))

    return render_template('bookings_history.html', user_bookings=expired_bookings, page='bookings_history')