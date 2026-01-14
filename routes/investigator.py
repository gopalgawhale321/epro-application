from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

from app import db
from models import PatientReport, User

investigator_bp = Blueprint('investigator', __name__)

@investigator_bp.route('/investigator/dashboard')
@login_required
def dashboard():
    if current_user.role != 'investigator':
        return redirect(url_for('patient.dashboard'))
    
    # Get urgent reports
    urgent_reports = PatientReport.query.filter_by(is_urgent=True, alert_sent=False)\
                                      .order_by(PatientReport.timestamp.desc())
    
    # Get recent reports
    recent_reports = PatientReport.query.order_by(PatientReport.timestamp.desc()).limit(10).all()
    
    # Get patient count
    patient_count = User.query.filter_by(role='patient').count()
    
    # Get report count for the last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_reports = PatientReport.query.filter(PatientReport.timestamp >= week_ago).count()
    
    return render_template('investigator/dashboard.html',
                         urgent_reports=urgent_reports,
                         recent_reports=recent_reports,
                         patient_count=patient_count,
                         weekly_reports=weekly_reports)

@investigator_bp.route('/investigator/reports')
@login_required
def reports():
    if current_user.role != 'investigator':
        return redirect(url_for('patient.dashboard'))
    
    # Get filter parameters
    patient_id = request.args.get('patient_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    urgent_only = request.args.get('urgent') == 'on'
    
    # Build query
    query = PatientReport.query
    
    if patient_id:
        query = query.filter(PatientReport.patient_id.ilike(f'%{patient_id}%'))
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(PatientReport.timestamp >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(PatientReport.timestamp <= end_date)
    
    if urgent_only:
        query = query.filter_by(is_urgent=True)
    
    reports = query.order_by(PatientReport.timestamp.desc()).all()
    
    return render_template('investigator/reports.html', reports=reports)

@investigator_bp.route('/investigator/patient/<patient_id>')
@login_required
def patient_details(patient_id):
    if current_user.role != 'investigator':
        return redirect(url_for('patient.dashboard'))
    
    # Get patient's reports
    reports = PatientReport.query.filter_by(patient_id=patient_id)\
                               .order_by(PatientReport.timestamp.desc())\
                               .all()
    
    if not reports:
        flash('No reports found for this patient.', 'warning')
        return redirect(url_for('investigator.reports'))
    
    # Get patient info
    patient = User.query.filter_by(username=patient_id, role='patient').first()
    
    # Create trend data
    dates = [r.timestamp.strftime('%Y-%m-%d') for r in reports]
    pain_scores = [r.pain for r in reports]
    fatigue_scores = [r.fatigue for r in reports]
    
    # Create a simple plot
    plt.figure(figsize=(10, 4))
    plt.plot(dates, pain_scores, label='Pain (0-10)', marker='o')
    plt.plot(dates, fatigue_scores, label='Fatigue (0-10)', marker='s')
    plt.title(f'Symptom Trends for Patient {patient_id}')
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Save plot to a bytes buffer
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    return render_template('investigator/patient_details.html',
                         patient=patient,
                         reports=reports,
                         plot_url=plot_url)

@investigator_bp.route('/investigator/acknowledge_alert/<int:report_id>', methods=['POST'])
@login_required
def acknowledge_alert(report_id):
    if current_user.role != 'investigator':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    report = PatientReport.query.get_or_404(report_id)
    report.alert_sent = True
    db.session.commit()
    
    return jsonify({'status': 'success'})
