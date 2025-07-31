from .database import db

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(),unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    Name= db.Column(db.String())
    address= db.Column(db.String())
    pincode= db.Column(db.String())
    type = db.Column(db.String(), default='general')
    


class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    locname = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    price = db.Column(db.Float, nullable=False)
    maxspots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot', cascade="all, delete", lazy=True)


class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(1), nullable=False, default="A")  # 'O' = Occupied, 'A' = Available
    customer_id = db.Column(db.Integer, nullable=True)
    vehicle_number = db.Column(db.String(20), nullable=True)
    time_of_parking = db.Column(db.Integer, nullable=True)  # user-entered hours
    estimated_cost = db.Column(db.Float, nullable=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)