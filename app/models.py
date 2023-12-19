from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    garage = db.relationship('Car', backref='owner', lazy='dynamic')
    role = db.Column(db.String(20), default='user')  

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def change_username(self, new_username):
        self.username = new_username

    def formatted_registration_date(self):
        if self.registration_date:
            return self.registration_date.strftime('%Y-%m-%d')
        elif self.registration_date == None:
            return None
        else:
            return "N/A"
        
    def user_revenue(self):
        total_revenue = 0
        for booking in Booking.query.filter_by(user_id=self.id).all():
            total_revenue += booking.money
        return total_revenue
    
    def delete_user(self):
        try:
            # Step 1: Remove all bookings associated with the user
            bookings_to_remove = Booking.query.filter_by(user_id=self.id).all()
            for booking in bookings_to_remove:
                Booking.remove_booking(booking.id)

            # Step 2: Delete all cars owned by the user
            cars_to_remove = Car.query.filter_by(user_id=self.id).all()
            for car in cars_to_remove:
                Car.delete_car(car.plate)

            # Step 3: Delete the user itself
            db.session.delete(self)
            db.session.commit()
            
            return True
        except SQLAlchemyError as e:
            print(f"Error deleting user: {str(e)}")
            db.session.rollback()
            return False
        
        
    
class Car(db.Model):
    plate = db.Column(db.String(8), primary_key=True, index=True, unique=True)
    make = db.Column(db.String(15), index=True)
    model = db.Column(db.String(15), index=True)
    fuel = db.Column(db.String(8), index=True)
    year = db.Column(db.Integer, index=True)
    cc = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    days = db.Column(db.Integer, default=0, index=True)
    money = db.Column(db.Integer, default=0, index=True)

    @classmethod
    def search(cls, search_query, search_type, current_user_id):
        # Handle the "plate" field separately to keep it all uppercase
        if search_type == 'plate':
            search_query = search_query.upper()
        
        # Convert other fields to lowercase and capitalize the first letter
        else:
            search_query = search_query.lower().capitalize()

        # Perform the search and filter the cars based on the query and type
        if search_type == 'plate':
            filtered_cars = []
            cars = Car.query.filter_by(user_id=current_user_id).all()
            for car in cars:
                if search_query in car.plate:
                    filtered_cars.append(car)
        elif search_type == 'make':
            filtered_cars = Car.query.filter_by(make=search_query, user_id=current_user_id).all()
        elif search_type == 'model':
            filtered_cars = Car.query.filter_by(model=search_query, user_id=current_user_id).all()
        elif search_type == 'fuel':
            filtered_cars = Car.query.filter_by(fuel=search_query, user_id=current_user_id).all()
        elif search_type == 'year':
            filtered_cars = Car.query.filter_by(year=search_query, user_id=current_user_id).all()
        elif search_type == 'cc':
            filtered_cars = Car.query.filter_by(cc=search_query, user_id=current_user_id).all()
        else:
            filtered_cars = []

        return filtered_cars
    
    def amend_car(self, car_plate, car_make, car_model, car_fuel, car_year, car_cc):
        try:
            self.plate = car_plate
            self.make = car_make
            self.model = car_model
            self.year = car_year
            self.fuel = car_fuel
            self.cc = car_cc

            db.session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error amending car: {str(e)}")

    @classmethod
    def delete_car(cls, car_plate):
        try:
            car = cls.query.get(car_plate)
            if car:
                db.session.delete(car)
                db.session.commit()
                return True
            else:
                return False
        except SQLAlchemyError as e:
            print(f"Error removing car: {str(e)}")
            db.session.rollback()
            return False

    # Reset days and money for every car at the beginning of every year
    @classmethod
    def reset_parameters(cls):
        today = datetime.now()
        if today.month == 1 and today.day == 1:
            for car in Car.query.all():
                car.days = 0
                car.money = 0

            db.session.commit()

    def __repr__(self):
        return f'<Car: {self.plate}, {self.make}, {self.model}, {self.cc}, {self.fuel}, {self.year}>'
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    car_plate = db.Column(db.String(8), db.ForeignKey('car.plate'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note = db.Column(db.String(160))
    money = db.Column(db.Integer, default=0, index=True)
    
    # Add a reference to the Car model for easier access
    car = db.relationship('Car', backref='bookings', lazy=True)

    @staticmethod
    def create_booking(car_plate, price, start_datetime, end_datetime, user_id, note):
        # Check if the selected car exists
        car = Car.query.filter_by(plate=car_plate).first()
        if not car:
            raise ValueError(f'Car with plate {car_plate} not found.')

        try:
            # Check for overlapping bookings
            overlapping_booking = Booking.query.filter(
                Booking.car_plate == car_plate,
                Booking.start_datetime < end_datetime,
                Booking.end_datetime > start_datetime
            ).first()

            if overlapping_booking:
                return None, overlapping_booking.start_datetime, overlapping_booking.end_datetime
            
            # Calculate booking duration
            booking_duration = (end_datetime - start_datetime).days + 1 # It adds a day because a booking within the same day counts as zero days.

            # Create a new booking
            booking = Booking(
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                car_plate=car_plate,
                user_id=user_id,
                note=note,
                money=price
            )

            db.session.add(booking)
            car.days += booking_duration
            car.money += price
            db.session.commit()

            return booking, None, None
        except SQLAlchemyError as e:
            print(f"Error during booking creation: {str(e)}")
            db.session.rollback()
            raise e

    @classmethod
    def remove_booking(cls, booking_id):
        try:
            booking = cls.query.get(booking_id)
            if booking:
                # Calculate booking duration
                booking_duration = (booking.end_datetime - booking.start_datetime).days + 1
                car = Car.query.filter_by(plate=booking.car_plate).first()

                db.session.delete(booking)

                # Check if the booking is active, otherwise no days/money are subtracted 
                if booking.end_datetime > datetime.now():
                    car.days -= booking_duration
                    car.money -= booking.money

                db.session.commit()
                return True
            else:
                return False
        except SQLAlchemyError as e:
            print(f"Error removing booking: {str(e)}")
            db.session.rollback()
            return False

    def __repr__(self):
        return f'<Booking: {self.id}, Plate: {self.car_plate}, User: {self.user_id}, Note: {self.note}>'
        
    def amend_booking(self, start_datetime, end_datetime, note):
        if start_datetime >= end_datetime:
            raise ValueError("End date must be after start date.")

        # Update booking information
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.note = note

        # Save changes to the database
        db.session.commit()
    
