from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from app import login
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from datetime import datetime
from time import time
import jwt
from app import app

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    garage = db.relationship('Car', backref='owner_garage', lazy='dynamic')
    groups = db.relationship('Groups', backref='owner_groups', lazy='dynamic')
    contacts = db.relationship('Contacts', backref='owner_contacts', lazy='dynamic')
    role = db.Column(db.String(20), default='user')  
    currency = db.Column(db.String(1), default='€')
    measurement_unit = db.Column(db.String(5), default='Km')
    language = db.Column(db.String(2), default='en')
    is_verified = db.Column(db.Boolean, default=True)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)
    
    def get_verification_token(self, expires_in=600):
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_verification_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['verify_email']
        except:
            return
        return db.session.query(User).get(id)

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
    
    def change_preferences(self, currency, measurement_unit, language):
        self.currency = currency
        self.measurement_unit = measurement_unit
        self.language = language

        db.session.commit()
    
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

            # Step 3: Delete all user's contacts
            contacts_to_remove = Contacts.query.filter_by(user_id=self.id).all()
            for contact in contacts_to_remove:
                db.session.delete(contact)
                db.session.commit()

            # Step 3: Delete the user itself
            db.session.delete(self)
            db.session.commit()
            
            return True
        except SQLAlchemyError as e:
            print(f"Error deleting user: {str(e)}")
            db.session.rollback()
            return False
        
class Renewal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.String(8), db.ForeignKey('car.plate'))
    renewal_type = db.Column(db.String(50))  # e.g., 'MOT', 'Insurance'
    renewal_date = db.Column(db.Date)        # Date of the renewal
    renewal_expiry = db.Column(db.Date)      # New expiry date
    renewal_cost = db.Column(db.Float)
    description = db.Column(db.String(160))

    @classmethod
    def latest_renewal(cls, car_id, renewal_type):
        '''lista = cls.query.filter_by(car_id=car_id, renewal_type=renewal_type)\
                            .order_by(desc(cls.renewal_expiry)).all()
        for x in lista:
            print(x.renewal_expiry)'''
        # Query the database for renewals of the specified type for the given car,
        # order them by renewal date in descending order (latest first),
        # and retrieve the first (latest) renewal, or return None if no renewals are found
        latest = cls.query.filter_by(car_id=car_id, renewal_type=renewal_type)\
                            .order_by(desc(cls.renewal_expiry)).first()

        if latest:
            return latest.renewal_expiry
        else:
            return None
    
class Car(db.Model):
    plate = db.Column(db.String(8), primary_key=True, index=True, unique=True)
    make = db.Column(db.String(15), index=True)
    model = db.Column(db.String(15), index=True)
    fuel = db.Column(db.String(8), index=True)
    year = db.Column(db.Integer, index=True)
    cc = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    days = db.Column(db.Integer, default=0, index=True)
    money = db.Column(db.Integer, default=0, index=True) # Referred as 'revenue'
    car_cost = db.Column(db.Integer, default=0, index=True)
    insurance_cost = db.Column(db.Float, default=0, index=True)
    insurance_expiry_date = db.Column(db.DateTime)
    mot_cost = db.Column(db.Float, default=0, index=True)
    mot_expiry_date = db.Column(db.DateTime)
    road_tax_cost = db.Column(db.Float, default=0, index=True)
    road_tax_expiry_date = db.Column(db.DateTime)
    renewal = db.relationship('Renewal', backref='car', lazy='dynamic')
    km = db.Column(db.Integer, default=0, index=True)

    def add_renewal(self, renewal_type, renewal_date, renewal_cost, current_datetime, description=None):
        renewal = Renewal(
            car_id=self.plate,
            renewal_type=renewal_type,
            renewal_date=current_datetime,
            renewal_expiry=renewal_date,
            renewal_cost=renewal_cost,
            description=description
        )
        db.session.add(renewal)
        db.session.commit()

        if renewal_date.date() < Renewal.latest_renewal(self.plate, renewal_type):
            renewal_date = Renewal.latest_renewal(self.plate, renewal_type)

        if renewal_type == 'insurance':
            self.insurance_expiry_date = renewal_date
            self.insurance_cost += renewal_cost
            self.car_cost += renewal_cost
            db.session.commit()

        if renewal_type == 'mot':
            self.mot_expiry_date = renewal_date
            self.mot_cost += renewal_cost
            self.car_cost += renewal_cost
            db.session.commit()

        if renewal_type == 'road_tax':
            self.road_tax_expiry_date = renewal_date
            self.road_tax_cost += renewal_cost
            self.car_cost += renewal_cost
            db.session.commit()

        if renewal_type == 'other':
            self.car_cost += renewal_cost
            db.session.commit()
    
    def delete_renewal(self, renewal_id):
        renewal = Renewal.query.filter_by(car_id=self.plate, id=renewal_id).first()
        renewal_type = renewal.renewal_type
        renewal_cost = renewal.renewal_cost
        try:
            db.session.delete(renewal)
            db.session.commit()
            if renewal_type == 'insurance':
                self.insurance_expiry_date = Renewal.latest_renewal(self.plate, renewal_type)
                self.insurance_cost -= renewal_cost
                self.car_cost -= renewal_cost
                db.session.commit()

            if renewal_type == 'mot':
                self.mot_expiry_date = Renewal.latest_renewal(self.plate, renewal_type)
                self.mot_cost -= renewal_cost
                self.car_cost -= renewal_cost
                db.session.commit()

            if renewal_type == 'road_tax':
                self.road_tax_expiry_date = Renewal.latest_renewal(self.plate, renewal_type)
                self.road_tax_cost -= renewal_cost
                self.car_cost -= renewal_cost
                db.session.commit()

            if renewal_type == 'other':
                self.car_cost -= renewal_cost
                db.session.commit()
        except SQLAlchemyError as e:
            print(f"Error finding the renewal: {str(e)}")
        return True        

    def get_renewal(self, renewal_type=None):
        if renewal_type:
            return Renewal.query.filter_by(car_id=self.plate, renewal_type=renewal_type).all()
        return Renewal.query.filter_by(car_id=self.plate).all()

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
    
    def amend_car(self, car_plate, car_make, car_model, car_fuel, car_year, car_cc): #mancano road tax etc..
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
    km = db.Column(db.Integer, default=0, index=True) # Car's kilometres when booking
    
    # Add a reference to the Car model for easier access
    car = db.relationship('Car', backref='bookings', lazy=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id', name='booking_contacts_id'), nullable=True)
    
    # Define the foreign key relationship with the Groups model
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', name='booking_group'), nullable=True)
    group = db.relationship('Groups', back_populates='bookings', lazy=True)

    def get_booking_info(self):
        # Generate a string containing detailed booking information.
        booking_info = f"Booking ID: {self.id}\n"
        booking_info += f"Start Date: {self.start_datetime.strftime('%d/%m, %H:%M')}\n"
        booking_info += f"End Date: {self.end_datetime.strftime('%d/%m, %H:%M')}\n"
        if self.note:
            booking_info += f"Note: {self.note}\n"
        if self.group:
            booking_info += f"Note: {self.group}\n"
        return booking_info

    @staticmethod
    def create_booking(car_plate, price, start_datetime, end_datetime, contact_id, user_id, note, km=0, group_id=None):
        # Check if the selected car and contact exist
        car = Car.query.filter_by(plate=car_plate).first()
        contact = Contacts.query.filter_by(id=contact_id).first()
        if group_id:
            group = Groups.query.filter_by(id=group_id).first()
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
                money=price,
                contact_id=contact_id if contact else None,
                group_id=group.id if group else None,
                km=km
            )

            db.session.add(booking)
            car.km = booking.km
            car.days += booking_duration            
            car.money += price
            
            if contact:
                contact.rented_days += booking_duration
                contact.money_spent += price
            if group:
                group.money += price
                group.bookings_number += 1
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

    def is_expired(self):
        current_datetime = datetime.now()
        return self.end_datetime < current_datetime
    
    def booking_duration(self):
        booking_duration = (self.end_datetime - self.start_datetime).days + 1 # It adds a day because a booking within the same day counts as zero days.
        return booking_duration
    
class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), index=True)
    driver_licence_n = db.Column(db.String(20), index=True)
    dob = db.Column(db.String(10), index=True)
    telephone = db.Column(db.String(20), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='contacts_user_id'), nullable=False)
    bookings = db.relationship('Booking', backref='owner', lazy='dynamic')
    money_spent = db.Column(db.Integer, default=0, index=True)
    rented_days = db.Column(db.Integer, default=0, index=True)
    town_of_birth = db.Column(db.String(100), index=True)
    city_of_residence = db.Column(db.String(100), index=True)
    address = db.Column(db.String(255), index=True)

    @staticmethod
    def add_contact(full_name, dob, driver_licence_n, telephone, town_of_birth,  city_of_residence, address, user_id):
        new_contact = Contacts(
            full_name = full_name,
            driver_licence_n = driver_licence_n,
            dob = dob,
            telephone = telephone,
            town_of_birth = town_of_birth,
            city_of_residence = city_of_residence,
            address = address,
            user_id = user_id
        )

        db.session.add(new_contact)
        db.session.commit()

    @classmethod
    def search(cls, search_query, current_user_id):
        # Perform a case-insensitive search on the 'full_name' field
        search_results = cls.query.filter(
            (cls.full_name.ilike(f"%{search_query}%")) &
            (cls.user_id == current_user_id)
        ).all()

        return search_results
    
    @classmethod
    def search_contacts(cls, search_type, search_query, user_id):
        # Build filter conditions dynamically based on search criteria
        filter_conditions = cls.build_filter_conditions(search_type, search_query, user_id)

        # Apply filter conditions and return the search results
        return cls.query.filter(*filter_conditions).all()

    @classmethod
    def build_filter_conditions(cls, search_type, search_query, user_id):
        if search_type == 'full_name':
            # Case-insensitive search on the 'full_name' field
            return cls.full_name.ilike(f"%{search_query}%"), cls.user_id == user_id
        elif search_type == 'driver_licence':
            # Exact match on the 'driver_licence_n' field
            return cls.driver_licence_n == search_query, cls.user_id == user_id
        elif search_type == 'dob':
            # Exact match on the 'dob' field
            return cls.dob == search_query, cls.user_id == user_id
        elif search_type == 'id':
            # Exact match on the 'id' field
            return cls.id == search_query, cls.user_id == user_id
        else:
            # Invalid search type, return an invalid condition to produce an empty result
            return cls.user_id == -1  # Assuming an invalid condition#
        
class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    telephone = db.Column(db.String(20), default='/', index=True)
    money = db.Column(db.Integer, default=0, index=True)
    bookings_number = db.Column(db.Integer, default=0, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookings = db.relationship('Booking', back_populates='group', lazy='dynamic')
    
    @staticmethod
    def add_group(name, telephone, user_id):
        new_group = Groups(
            name = name,
            telephone = telephone,
            user_id = user_id
        )

        db.session.add(new_group)
        db.session.commit()

    @classmethod
    def search_groups(cls, search_type, search_query, user_id):
        # Build filter conditions dynamically based on search criteria
        filter_conditions = cls.build_filter_conditions(search_type, search_query, user_id)

        # Apply filter conditions and return the search results
        return cls.query.filter(*filter_conditions).all()

    @classmethod
    def build_filter_conditions(cls, search_type, search_query, user_id):
        if search_type == 'name':
            # Case-insensitive search on the 'name' field
            return cls.name.ilike(f"%{search_query}%"), cls.user_id == user_id
        elif search_type == 'telephone':
            # Exact match on the 'driver_licence_n' field
            return cls.telephone == search_query, cls.user_id == user_id
        elif search_type == 'id':
            # Exact match on the 'id' field
            return cls.id == search_query, cls.user_id == user_id
        else:
            # Invalid search type, return an invalid condition to produce an empty result
            return cls.user_id == -1  # Assuming an invalid condition