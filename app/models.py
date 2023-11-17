from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import UniqueConstraint

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

    def __repr__(self):
        return f'<Car: {self.plate}, {self.make}, {self.model}, {self.cc}, {self.fuel}, {self.year}>'
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    car_plate = db.Column(db.String(8), db.ForeignKey('car.plate'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Add a reference to the Car model for easier access
    car = db.relationship('Car', backref='bookings', lazy=True)

    @staticmethod
    def create_booking(car_plate, start_datetime, end_datetime, user_id):
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
        
        except SQLAlchemyError as e:
            print(f"Error during query: {str(e)}")
            raise e

        if overlapping_booking:
            raise ValueError('Selected car is already booked for the specified period.')

        # Create a new booking
        booking = Booking(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            car_plate=car_plate,
            user_id=user_id
        )

        db.session.add(booking)
        db.session.commit()

        return booking

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
        return f'<Booking {self.id}>' 
    
