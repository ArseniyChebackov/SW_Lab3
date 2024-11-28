from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(200), nullable=True)
    specialties = db.Column(db.String(500), nullable=True)