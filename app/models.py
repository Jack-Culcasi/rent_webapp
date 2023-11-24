from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy.exc import SQLAlchemyError

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    garage = db.relationship('Car', backref='owner', lazy='dynamic') 

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Car(db.Model):
    plate = db.Column(db.String(8), primary_key=True, index=True, unique=True)
    make = db.Column(db.String(15), index=True)
    model = db.Column(db.String(15), index=True)
    fuel = db.Column(db.String(8), index=True)
    year = db.Column(db.Integer, index=True)
    cc = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

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
            filtered_cars = Car.query.filter_by(plate=search_query, user_id=current_user_id).all()
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

    def __repr__(self):
        return f'<Car: {self.plate}, {self.make}, {self.model}, {self.cc}, {self.fuel}, {self.year}>'
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    car_plate = db.Column(db.String(8), db.ForeignKey('car.plate'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note = db.Column(db.String(160))
    
    # Add a reference to the Car model for easier access
    car = db.relationship('Car', backref='bookings', lazy=True)

    @staticmethod
    def create_booking(car_plate, start_datetime, end_datetime, user_id, note):
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

            # Create a new booking
            booking = Booking(
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                car_plate=car_plate,
                user_id=user_id,
                note=note
            )
            db.session.add(booking)
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
                db.session.delete(booking)
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
    
