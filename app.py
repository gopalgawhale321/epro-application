from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os

from config import Config
from models import db, User, PatientReport

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    # Create a default investigator user if not exists
    if not User.query.filter_by(username='investigator').first():
        admin = User(
            username='investigator',
            role='investigator'
        )
        admin.set_password('demo123')
        db.session.add(admin)
        db.session.commit()

# Import routes after app and db are created to avoid circular imports
from routes.patient import patient_bp
from routes.investigator import investigator_bp

# Register blueprints
app.register_blueprint(patient_bp, url_prefix='')
app.register_blueprint(investigator_bp, url_prefix='/investigator')

# Main routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'investigator':
            return redirect(url_for('investigator.dashboard'))
        return redirect(url_for('patient.dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Helper function to check for urgent conditions
def check_urgent_conditions(report):
    is_urgent = False
    reasons = []
    
    if report.nausea == 'Severe':
        is_urgent = True
        reasons.append('Severe nausea reported')
    
    if report.pain and report.pain >= 7:
        is_urgent = True
        reasons.append(f'High pain score: {report.pain}/10')
    
    if report.has_chest_pain:
        is_urgent = True
        reasons.append('Chest pain reported')
    
    if report.has_breathing_difficulty:
        is_urgent = True
        reasons.append('Breathing difficulty reported')
    
    # Check vitals if provided
    if report.heart_rate and (report.heart_rate < 50 or report.heart_rate > 120):
        is_urgent = True
        reasons.append(f'Abnormal heart rate: {report.heart_rate} bpm')
    
    if report.blood_pressure:
        try:
            sys, dia = map(int, report.blood_pressure.split('/'))
            if sys > 180 or dia > 120 or sys < 90 or dia < 60:
                is_urgent = True
                reasons.append(f'Abnormal blood pressure: {report.blood_pressure} mmHg')
        except (ValueError, AttributeError):
            pass
    
    return is_urgent, reasons

if __name__ == '__main__':
    app.run(debug=True)
