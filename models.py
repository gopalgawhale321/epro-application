from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'investigator'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PatientReport(db.Model):
    __tablename__ = 'patient_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Symptoms
    nausea = db.Column(db.String(20))  # None/Mild/Moderate/Severe
    fatigue = db.Column(db.Integer)    # 0-10 scale
    pain = db.Column(db.Integer)       # 0-10 scale
    
    # Adverse effects
    has_rash = db.Column(db.Boolean, default=False)
    has_breathing_difficulty = db.Column(db.Boolean, default=False)
    has_chest_pain = db.Column(db.Boolean, default=False)
    has_swelling = db.Column(db.Boolean, default=False)
    has_fever = db.Column(db.Boolean, default=False)
    
    # Medication adherence
    missed_dose = db.Column(db.Boolean, default=False)
    
    # Vitals (optional)
    blood_pressure = db.Column(db.String(10))
    heart_rate = db.Column(db.Integer)
    blood_glucose = db.Column(db.Float)
    
    # Additional notes
    comments = db.Column(db.Text)
    
    # Classification
    is_urgent = db.Column(db.Boolean, default=False)
    alert_sent = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'timestamp': self.timestamp.isoformat(),
            'nausea': self.nausea,
            'fatigue': self.fatigue,
            'pain': self.pain,
            'has_rash': self.has_rash,
            'has_breathing_difficulty': self.has_breathing_difficulty,
            'has_chest_pain': self.has_chest_pain,
            'has_swelling': self.has_swelling,
            'has_fever': self.has_fever,
            'missed_dose': self.missed_dose,
            'blood_pressure': self.blood_pressure,
            'heart_rate': self.heart_rate,
            'blood_glucose': self.blood_glucose,
            'comments': self.comments,
            'is_urgent': self.is_urgent
        }
