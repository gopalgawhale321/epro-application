from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from models import PatientReport
from app import check_urgent_conditions

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/patient/dashboard')
@login_required
def dashboard():
    if current_user.role != 'patient':
        return redirect(url_for('investigator.dashboard'))
    
    # Get recent reports for this patient
    reports = PatientReport.query.filter_by(patient_id=current_user.username)\
                               .order_by(PatientReport.timestamp.desc())\
                               .limit(5).all()
    
    return render_template('patient/dashboard.html', reports=reports)

@patient_bp.route('/patient/report', methods=['GET', 'POST'])
@login_required
def submit_report():
    if current_user.role != 'patient':
        return redirect(url_for('investigator.dashboard'))
    
    if request.method == 'POST':
        # Create a new report
        report = PatientReport(
            patient_id=current_user.username,
            nausea=request.form.get('nausea'),
            fatigue=int(request.form.get('fatigue', 0)),
            pain=int(request.form.get('pain', 0)),
            has_rash='rash' in request.form,
            has_breathing_difficulty='breathing_difficulty' in request.form,
            has_chest_pain='chest_pain' in request.form,
            has_swelling='swelling' in request.form,
            has_fever='fever' in request.form,
            missed_dose='missed_dose' in request.form,
            blood_pressure=request.form.get('blood_pressure'),
            heart_rate=int(request.form.get('heart_rate')) if request.form.get('heart_rate') else None,
            blood_glucose=float(request.form.get('blood_glucose')) if request.form.get('blood_glucose') else None,
            comments=request.form.get('comments')
        )
        
        # Check for urgent conditions
        is_urgent, reasons = check_urgent_conditions(report)
        report.is_urgent = is_urgent
        
        # Save to database
        db.session.add(report)
        db.session.commit()
        
        if is_urgent:
            flash('Your report has been submitted. Please note that some symptoms require urgent attention and the investigator has been notified.', 'warning')
        else:
            flash('Your report has been submitted successfully.', 'success')
        
        return redirect(url_for('patient.dashboard'))
    
    return render_template('patient/report_form.html')

@patient_bp.route('/api/patient/reports')
@login_required
def get_reports():
    if current_user.role != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
    
    reports = PatientReport.query.filter_by(patient_id=current_user.username)\
                               .order_by(PatientReport.timestamp.desc())\
                               .all()
    
    return jsonify([{
        'date': report.timestamp.strftime('%Y-%m-%d'),
        'nausea': report.nausea,
        'fatigue': report.fatigue,
        'pain': report.pain,
        'is_urgent': report.is_urgent
    } for report in reports])
