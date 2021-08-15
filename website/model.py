from . import db
from flask_login import UserMixin


class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(225), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(14), nullable=False)
    role = db.Column(db.Integer , nullable=False)
    isDeleted = db.Column(db.Boolean, nullable=False, default=False)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(8), unique=True)
    brand = db.Column(db.String(100), nullable=False)
    brand_model = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    isDeleted = db.Column(db.Boolean, nullable=False, default=False)

class Repairs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    period = db.Column(db.Date, nullable=False) #dd/mm/yyyy
    isServiced = db.Column(db.Boolean, nullable=False)
    last_service_mileage = db.Column(db.Integer,nullable=False)
    current_service_mileage = db.Column(db.Integer, nullable=False)
    km_covered = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.Numeric, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    attachment = db.Column(db.Text, nullable=True)
    isDeleted = db.Column(db.Boolean, nullable=False, default=False)
class Fuel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    period = db.Column(db.Date, nullable=False) #dd/mm/yyyy
    opening_km = db.Column(db.Integer, nullable=False)
    closing_km = db.Column(db.Integer, nullable=False)
    total_Qty_purchased_ltrs = db.Column(db.Numeric, nullable=False)
    total_Qty_purchased_ngn = db.Column(db.Numeric, nullable=False)
    avg_price = db.Column(db.Numeric, nullable=False)
    attachment = db.Column(db.Text, nullable=True)
    comments =  db.Column(db.Text, nullable=True)
    isDeleted = db.Column(db.Boolean, nullable=False, default=False)
    