#Flask imports
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import calendar as cal

# Local imports
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Car, Booking, Contacts

                                                                                # Users Login/Logout/Profile/Admin

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('overview')) 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', "error")
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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile(): 
    if request.method == 'POST':
        if 'username' in request.form:
            new_username = request.form.get('username')
            existing_username = User.query.filter_by(username=new_username).first()
            if existing_username:
                flash(f'{existing_username.username} already taken, please choose another one', 'error')
                return redirect(url_for('profile'))
            else:
                current_user.change_username(new_username)
                db.session.commit()
                flash('Username successfully changed!', 'success')
                return redirect(url_for('profile'))                
                
        elif 'email' in request.form:
            new_email = request.form.get('email')
            existing_email = User.query.filter_by(email=new_email).first()
            if existing_email:
                flash(f'{existing_email.email} already taken, please choose another one', 'error')
                return redirect(url_for('profile'))
            else:
                current_user.email = new_email
                db.session.commit()
                flash('Email successfully changed!', 'success')
                return redirect(url_for('profile'))   
            
        elif 'password' in request.form:        
            new_password = request.form.get('password')
            password_confirm = request.form.get('confirm_password')

            if new_password == password_confirm:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password successfully changed!', 'success')
                return redirect(url_for('profile'))  
            else:
                flash('Passwords do not match!', 'error') 
                return redirect(url_for('profile'))  
            
        elif 'delete_account' in request.form:
            user_to_delete = User.query.get(current_user.id)
            if user_to_delete:
                user_to_delete.delete_user()
                db.session.commit()
                flash('User succefully deleted!', 'success')
                return redirect(url_for('login'))
            else:
                return flash('User not found!', 'error')          
        return render_template('user.html', page='users_page', user=user) 

    return render_template('profile.html', title='Profile', page='profile', user=current_user, 
                           user_name=current_user.username if current_user.is_authenticated else None)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin(): 
    if current_user.username == 'admin' and current_user.role == 'admin':
        users = User.query.all()
        cars = Car.query.all()
        bookings = Booking.query.all()
        revenue = 0
        for booking in bookings:
            revenue += booking.money
        return render_template('admin.html', page='admin', total_users=len(users), total_cars=len(cars), total_bookings=len(bookings), total_revenue=revenue)
    else:
        return render_template('404.html')
    
@app.route('/users_list', methods=['GET', 'POST'])
@login_required
def users_list(): 
    if current_user.username == 'admin' and current_user.role == 'admin':
        users = User.query.all()
        return render_template('users_list.html', page='users_list', users=users)
    else:
        return render_template('404.html')
    
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    if current_user.username == 'admin' and current_user.role == 'admin':
        user = User.query.filter_by(username=username).one()
        cars = Car.query.filter_by(user_id=user.id)
        bookings = Booking.query.filter_by(user_id=user.id)
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            user_to_delete = User.query.get(user_id)
            if user_to_delete:
                user_to_delete.delete_user()
                db.session.commit()
                flash('User succefully deleted!', 'success')
                return redirect(url_for('users_list'))
            else:
                return flash('User not found!', 'error')          
        return render_template('user.html', page='users_page', user=user, cars=cars, bookings=bookings)        
    else:
        return render_template('404.html')

                                                                                # Garage

@app.route('/garage_view', methods=['GET', 'POST'])
@login_required
def garage_view():
    user_cars = current_user.garage.all()
    return render_template('garage_view.html', title='Garage', 
                           page="garage_view", user_cars=user_cars, user_name=current_user.username if current_user.is_authenticated else None)

@app.route('/garage_manage', methods=['GET', 'POST'])
@login_required
def garage_manage(): # Add Car
    user_cars = current_user.garage.all()
    if request.method == 'POST':
       # Process the form data for a POST request
       plate = request.form.get('Plate').upper()
       make = request.form.get('Make').lower().capitalize()
       model = request.form.get('Model').lower().capitalize()
       fuel = request.form.get('Fuel').lower().capitalize()
       year = request.form.get('Year').lower().capitalize()
       cc = request.form.get('Cc').lower().capitalize()

       # Check if a car with the same plate and user_id already exists
       existing_car = Car.query.filter_by(plate=plate).first()

       if existing_car is not None:
           flash('A car with this plate already exists in the database', 'error')
           return redirect(url_for('garage_manage'))

       new_car = Car(plate=plate, make=make, model=model, fuel=fuel, year=year, cc=cc, user_id=current_user.id)

       db.session.add(new_car)
       db.session.commit()
       flash('Car added successfully', 'success')
       return redirect(url_for('garage_manage'))
    else:
       # Render the form for a GET request
       return render_template('garage_manage.html', title='Add Car', page="garage_manage", user_cars=user_cars,
                              user_name=current_user.username if current_user.is_authenticated else None)


@app.route('/search', methods=['GET', 'POST'])
def search():
    user_cars = current_user.garage.all()
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        search_type = request.form.get('search_type')
        select_car = request.form.get('select_car')

        # Perform search based on both search type and selected car
        if search_type and search_query:
            filtered_cars = Car.search(search_query, search_type, current_user.id)
        elif select_car and select_car != "blank":
            # If a car is selected, perform search based on the selected car
            filtered_cars = [Car.query.filter_by(plate=select_car).first()]
        else:
            # No valid search parameters provided
            filtered_cars = []

        return render_template('garage_manage.html', cars=filtered_cars, search_type=search_type, search_query=search_query, user_cars=user_cars)
    
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
    # Check if it is the first of the year, if it is it resets car.days and car.money
    Car.reset_parameters() 

    if request.method == 'POST':
        try:
            if 'book' in request.form:
                car_plate = request.form.get('car_selection')
                price = int(request.form.get('Price'))
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
                    car_plate, price, start_datetime, end_datetime, current_user.id, note
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
    # Chosen time frame if Input    
    else:
        from_datetime = datetime.strptime(f'{from_date}', '%Y-%m-%d')
        to_datetime = datetime.strptime(f'{to_date}', '%Y-%m-%d')
        #Include the full to_datetime
        to_datetime += timedelta(days=1)    

    # Fetch all bookings for the user within the specified time range
    user_bookings = Booking.query.filter(
                Booking.user_id == current_user.id,
                Booking.end_datetime >= from_datetime,
                Booking.start_datetime <= to_datetime,
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
    current_datetime = datetime.utcnow()

    # Handles the redirection from other pages
    car_plate = request.args.get('car_plate')
    if car_plate:
        # Retrieve active bookings for a given car
                car_active_bookings = Booking.query.filter(
                    (Booking.car_plate == car_plate) &
                    (Booking.end_datetime > current_datetime)
                ).all()

                # Retrieve past bookings for a given car
                car_past_bookings = Booking.query.filter(
                    (Booking.car_plate == car_plate) &
                    (Booking.end_datetime <= current_datetime)
                ).all()

                selected_car = Car.query.filter_by(plate=car_plate).first()
                return render_template('garage_car.html', title='Car', page="garage_car", user_cars=user_cars, car_object=selected_car,
                                        active_bookings=car_active_bookings, past_bookings=car_past_bookings,
                                        user_name=current_user.username if current_user.is_authenticated else None)

    if request.method == 'POST':
        try:
            if 'plate' in request.form:
                car_plate = request.form.get('plate')

                # Retrieve active bookings for a given car
                car_active_bookings = Booking.query.filter(
                    (Booking.car_plate == car_plate) &
                    (Booking.end_datetime > current_datetime)
                ).all()

                # Retrieve past bookings for a given car
                car_past_bookings = Booking.query.filter(
                    (Booking.car_plate == car_plate) &
                    (Booking.end_datetime <= current_datetime)
                ).all()

                car = Car.query.filter_by(plate=car_plate).first()
                return render_template('garage_car.html', title='Car', page="garage_car", user_cars=user_cars,
                                        car_object=car, active_bookings=car_active_bookings, past_bookings=car_past_bookings,
                                        user_name=current_user.username if current_user.is_authenticated else None)
            
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

                # Retrieve active bookings for a given car
                car_active_bookings = Booking.query.filter(
                    (Booking.car_plate == car_plate) &
                    (Booking.end_datetime > current_datetime)
                ).all()

                # Retrieve past bookings for a given car
                car_past_bookings = Booking.query.filter(
                    (Booking.car_plate == car_plate) &
                    (Booking.end_datetime <= current_datetime)
                ).all()

                selected_car = Car.query.filter_by(plate=car_plate).first()
                return render_template('garage_car.html', title='Car', page="garage_car", user_cars=user_cars, car_object=selected_car,
                                        active_bookings=car_active_bookings, past_bookings=car_past_bookings,
                                        user_name=current_user.username if current_user.is_authenticated else None)
                
        except ValueError as e:
            flash(str(e), 'error')
            print(f'ValueError: {str(e)}')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            print(f'Error: {str(e)}')

    return render_template('garage_car.html', title='Car', page="garage_car", user_cars=user_cars,
                           user_name=current_user.username if current_user.is_authenticated else None)

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

    return render_template('bookings_view.html', user_bookings=active_bookings, page='bookings_view',
                           user_name=current_user.username if current_user.is_authenticated else None)

@app.route('/bookings_manage', methods=['GET', 'POST'])
@login_required
def bookings_manage():
    current_date = datetime.utcnow()
    booking_id = request.args.get('booking_id')
    
    # Retrieve active bookings
    user_bookings = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (Booking.end_datetime > current_date)
    ).all()

    if booking_id:
        selected_booking = Booking.query.filter_by(id=booking_id).first()
        if selected_booking.is_expired():
            flash(f'Booking with ID {selected_booking.id} is no longer active, you can only delete it', 'error')
            return redirect(url_for('bookings_history'))
    else:
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

    return render_template('bookings_manage.html', page='bookings_manage', user_bookings=user_bookings, selected_booking=selected_booking,
                           user_name=current_user.username if current_user.is_authenticated else None)

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
            
        if request.form.get('delete_car'):
            booking_id = request.form.get('delete_car')
            # Modify the query to eagerly load the 'car' relationship
            selected_booking = Booking.query.options(db.joinedload(Booking.car)).filter_by(id=booking_id).first()
            if selected_booking:
                Booking.remove_booking(booking_id)
                flash('Booking successfully deleted!', 'success')

                # Redirect to the same page to refresh
                return redirect(url_for('garage_car'))
            
        if 'search' in request.form:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            searched_booking = []
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            #Include the full end_date
            end_date = end_date + timedelta(days=1)
            
            # Check booking which end date and start date is within the search
            for booking in expired_bookings:
                if booking.end_datetime >= start_date and booking.end_datetime <= end_date:
                    searched_booking.append(booking)
                elif booking.start_datetime >= start_date and booking.start_datetime <= end_date:
                    searched_booking.append(booking)

            return render_template('bookings_history.html', user_bookings=expired_bookings, page='bookings_history', bookings=searched_booking,
                                   user_name=current_user.username if current_user.is_authenticated else None)

    return render_template('bookings_history.html', user_bookings=expired_bookings, page='bookings_history',
                           user_name=current_user.username if current_user.is_authenticated else None)

                                                                                # Calendar

@app.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar(): 
    current_date = datetime.now()
    current_day = datetime.now().day
    current_month = datetime.now().strftime("%B %Y")
    first_day_of_month = current_date.replace(day=1)
    last_day_of_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    days_in_month = cal.monthrange(datetime.now().year, datetime.now().month)[1]


    user_bookings = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (Booking.start_datetime <= last_day_of_month) &
        (Booking.end_datetime >= first_day_of_month)
    ).all()

    user_cars = current_user.garage.all()
    return render_template('calendar.html', cars=user_cars, bookings=user_bookings, current_month=current_month, current_day=current_day,
                            days_in_month=days_in_month, user_name=current_user.username if current_user.is_authenticated else None)

@app.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts(): 
    user_contacts = current_user.contacts.all()

    if request.method == 'POST':
       # Process the form data for a POST request
       full_name = request.form.get('full_name')
       dob = request.form.get('dob')
       driver_licence_n = request.form.get('driver_licence_n')

       Contacts.add_contact(full_name, dob, driver_licence_n, current_user.id)
       flash('Contact added successfully', 'success')
       return redirect(url_for('contacts'))
    else:
       # Render the form for a GET request       
        return render_template('contacts.html', user_contacts=user_contacts, user_name=current_user.username if current_user.is_authenticated else None)
    
@app.route('/contact/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def contact_manage(contact_id):
    contact = Contacts.query.get_or_404(contact_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'amend':
            # Handle amendment logic
            contact.full_name = request.form.get('full_name')
            contact.dob = request.form.get('dob')
            contact.driver_licence_n = request.form.get('driver_licence_n')
            db.session.commit()
            flash('Contact details amended successfully', 'success')

        elif action == 'delete':
            # Handle deletion logic
            db.session.delete(contact)
            db.session.commit()
            flash('Contact deleted successfully', 'success')
            return redirect(url_for('contacts'))

    return render_template('contact_manage.html', contact=contact, user_name=current_user.username if current_user.is_authenticated else None)