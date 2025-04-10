from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app import db
from app.models import WebAppUser, Patient, AccessLevel, Treatments, Xray, HealthStatus, HealthWorker, XrayPrediction
from datetime import datetime
import os
from app.ml_model import analyse_xray

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def configure_upload_folder(app):
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def configure_upload_folder():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@routes.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    file_path = 'temp_xray.jpg'
    file.save(file_path)

    # Run prediction
    result = analyse_xray(file_path)

    # Clean up temp file
    os.remove(file_path)

    return result

@routes.route('/')
def homepage():
    # Render the homepage
    return render_template('homepage.html')

@routes.route('/admin/dashboard')
def admin_dashboard():
    # Render the admin dashboard
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.ADMIN:
        return "Unauthorized", 403
    return render_template('Adashboard.html')

@routes.route('/admin/database')
def admin_database():
    # Render the admin database page
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.ADMIN:
        return "Unauthorized", 403
    return render_template('Adatabase.html')

@routes.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Edit a specific user
    user = WebAppUser.query.get_or_404(user_id)
    return render_template('edit_user.html', user=user)

@routes.route('/admin/user_logs/<int:user_id>', methods=['GET'])
def user_logs(user_id):
    # View logs for a specific user
    user = WebAppUser.query.get_or_404(user_id)
    def get_user_logs(user_id):
        return [
            {"timestamp": datetime.now(), "action": "Login", "details": "User logged in."},
            {"timestamp": datetime.now(), "action": "Update", "details": "User updated profile."}
        ]
    logs = get_user_logs(user_id)
    return render_template('user_logs.html', user=user, logs=logs)

@routes.route('/admin/users')
def all_users():
    # View all users
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.ADMIN:
        return "Unauthorized", 403
    users = WebAppUser.query.all()
    return render_template('AllUsers.html', users=users)

@routes.route('/admin/search')
def admin_search():
    # Render the admin search page
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.ADMIN:
        return "Unauthorized", 403
    return render_template('Asearch.html')

@routes.route('/expert/dashboard')
def expert_dashboard():
    # Render the expert dashboard
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if not user or user.access_level != AccessLevel.EXPERT:
        return "Unauthorized", 403
    patients = Patient.query.all()
    return render_template('Edashboard.html', patients=patients)

@routes.route('/expert/patients')
def expert_patient_list():
    # View all patients for experts
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if not user or user.access_level != AccessLevel.EXPERT:
        return "Unauthorized", 403
    patients = Patient.query.all()
    return render_template('Eplist.html', patients=patients)

@routes.route('/expert/reports/<int:scan_id>')
def expert_reports(scan_id):
    # View reports for a specific scan
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.EXPERT:
        return "Unauthorized", 403
    xray = Xray.query.get_or_404(scan_id)
    patient_id = xray.patient_id
    return render_template('Ereports.html', xray=xray, patient_id=patient_id)

@routes.route('/expert/treatment/<int:patient_id>')
def expert_treatment(patient_id):
    # View treatment details for a specific patient
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.EXPERT:
        return "Unauthorized", 403
    patient = Patient.query.get_or_404(patient_id)
    return render_template('Etreat.html', patient=patient)

@routes.route('/expert/xrays/<int:patient_id>')
def expert_xrays(patient_id):
    # View X-rays for a specific patient
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.EXPERT:
        return "Unauthorized", 403
    patient = Patient.query.get_or_404(patient_id)
    xrays = Xray.query.filter_by(patient_id=patient_id).all()
    return render_template('Exrays.html', patient=patient, xrays=xrays)

@routes.route('/patient/register', methods=['GET', 'POST'])
def patient_register():
    # Register a new patient
    if request.method == 'POST':
        full_name = request.form.get('Fname')
        dob = request.form.get('Dob')
        address = request.form.get('HA')
        contact = request.form.get('Contact')
        email = request.form.get('email')
        next_of_kin = request.form.get('nok')
        next_of_kin_details = request.form.get('nokd')
        password = request.form.get('password')
        existing_user = WebAppUser.query.filter_by(login_username=email).first()
        if existing_user:
            flash("This email is already registered. Please use a different email.", "error")
            return render_template('Patientreg.html')
        new_user = WebAppUser(
            login_username=email,
            password=password, 
            access_level=AccessLevel.PATIENT
        )
        db.session.add(new_user)
        db.session.flush()
        new_patient = Patient(
            user_id=new_user.uid,
            name=full_name,
            dob=datetime.strptime(dob, "%Y-%m-%d"),
            address=address,
            contact=contact,
            next_of_kin=next_of_kin,
            next_of_kin_contact=next_of_kin_details,
            email=email,
            health_status=HealthStatus.GREEN,
            clinician_id=None
        )
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient registered successfully!", "success")
        session['user'] = email
        session['user_id'] = new_user.uid
        return redirect(url_for('routes.patient_dashboard'))
    return render_template('Patientreg.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    # Handle user login
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        user = WebAppUser.query.filter_by(login_username=email, password=password).first()
        
        if user:
            session['user'] = email
            session['user_id'] = user.uid
            if user.access_level == AccessLevel.HEALTH_WORKER:
                return redirect(url_for('routes.hw_dashboard'))
            elif user.access_level == AccessLevel.EXPERT:
                return redirect(url_for('routes.expert_dashboard'))
            elif user.access_level == AccessLevel.ADMIN:
                return redirect(url_for('routes.admin_dashboard'))
            elif user.access_level == AccessLevel.PATIENT:
                return redirect(url_for('routes.patient_dashboard'))
            else:
                flash("Invalid access level.", "error")
                return redirect(url_for('routes.login'))
        flash("Invalid credentials, please try again.", "error")
    return render_template('login.html')

@routes.route('/register_choice')
def register_choice():
    # Render the registration choice page
    return render_template('register_choice.html')

@routes.route('/health_worker/dashboard')
def hw_dashboard():
    # Render the health worker dashboard
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session.get('user')).first()
    if not user or user.access_level != AccessLevel.HEALTH_WORKER:
        return "Unauthorized", 403
    return render_template('HWdashboard.html', user=user)

@routes.route('/health_worker/profile')
def hw_profile():
    # View health worker profile
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.HEALTH_WORKER:
        return "Unauthorized", 403
    health_worker = HealthWorker.query.filter_by(user_id=user.uid).first()
    return render_template('HWprofile.html', health_worker=health_worker)

@routes.route('/health_worker/records')
def hw_records():
    # View records for health worker's patients
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if not user or user.access_level != AccessLevel.HEALTH_WORKER:
        return "Unauthorized", 403
    health_worker = HealthWorker.query.filter_by(user_id=user.uid).first()
    if not health_worker:
        flash("Health Worker profile not found. Please contact the administrator.", "error")
        return redirect(url_for('routes.hw_dashboard'))
    patients = Patient.query.filter_by(clinician_id=health_worker.id).all()
    return render_template('HWrecords.html', patients=patients)

@routes.route('/patient/dashboard')
def patient_dashboard():
    # Render the patient dashboard
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.PATIENT:
        return "Unauthorized", 403
    patient = Patient.query.filter_by(user_id=user.uid).first()
    return render_template('Pdashboard.html', patient=patient)

@routes.route('/patient/health_tips')
def patient_health_tips():
    # Render health tips for patients
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.PATIENT:
        return "Unauthorized", 403
    return render_template('Phealtips.html')

@routes.route('/ml_analysis/<int:scan_id>')
def ml_analysis(scan_id):
    # Perform ML analysis on a scan
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.HEALTH_WORKER:
        return "Unauthorized", 403
    xray = Xray.query.get_or_404(scan_id)
    return render_template('ml_analysis.html', scan_id=scan_id)

@routes.route('/patient/prescriptions')
def patient_prescriptions():
    # View prescriptions for a patient
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.PATIENT:
        return "Unauthorized", 403
    patient = Patient.query.filter_by(user_id=user.uid).first()
    treatments = Treatments.query.filter_by(patient_id=patient.patient_id).all()
    return render_template('prescriptions.html', treatments=treatments)

@routes.route('/patient/xrays')
def patient_xrays():
    # View X-rays for a patient
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.PATIENT:
        return "Unauthorized", 403
    patient = Patient.query.filter_by(user_id=user.uid).first()
    xrays = Xray.query.filter_by(patient_id=patient.patient_id).order_by(Xray.date_uploaded.desc()).all()
    return render_template('patient_xrays.html', xrays=xrays)

@routes.route('/patient-list')
def patient_list():
    # View a list of all patients
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level not in [AccessLevel.ADMIN, AccessLevel.EXPERT]:
        return "Unauthorized", 403
    patients = Patient.query.all()
    return render_template('patient_list.html', patients=patients)

@routes.route('/patient/support')
def patient_support():
    # Render the patient support page
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if user.access_level != AccessLevel.PATIENT:
        return "Unauthorized", 403
    return render_template('patient_support.html')

@routes.route('/health_worker/upload_xray', methods=['POST'])
def upload_xray():
    if 'user' not in session:
        return redirect(url_for('routes.login'))
    
    user = WebAppUser.query.filter_by(login_username=session['user']).first()
    if not user or user.access_level != AccessLevel.HEALTH_WORKER:
        return "Unauthorized", 403
    
    patient_id = request.form.get('patient_id')
    if not patient_id:
        flash("Patient ID is required.", "error")
        return redirect(url_for('routes.hw_dashboard'))
    
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if not patient:
        flash("Invalid Patient ID. Please check and try again.", "error")
        return redirect(url_for('routes.hw_dashboard'))
    
    xray_file = request.files.get('xray_file')
    if xray_file:
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{xray_file.filename}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        xray_file.save(upload_path)

        analysis_result = analyse_xray(upload_path)

        if "Pneumonia" in analysis_result:
            prediction = XrayPrediction.PNEUMONIA
        elif "Normal" in analysis_result:
            prediction = XrayPrediction.NORMAL
        else:
            prediction = XrayPrediction.UNCLEAR

        # Check if an existing X-ray record exists for the patient
        existing_xray = Xray.query.filter_by(patient_id=patient.patient_id).first()
        if existing_xray:
            existing_xray.image_path = upload_path
            existing_xray.date_uploaded = datetime.now()
            existing_xray.ml_prediction = prediction
            db.session.commit()
            flash("Existing X-ray record updated successfully.", "success")
        else:
            # Create a new Xray record
            new_xray = Xray(
                patient_id=patient.patient_id,  # Associate the X-ray with the patient
                health_worker_id=user.uid,
                image_path=upload_path,
                date_uploaded=datetime.now(),
                ml_prediction=prediction
            )
            db.session.add(new_xray)
            db.session.commit()

        return render_template('MLdisplayed.html', result=analysis_result)

    flash("Failed to upload X-ray. Please try again.", "error")
    return redirect(url_for('routes.hw_dashboard'))

@routes.route('/logout')
def logout():
    # Log out the user
    session.pop('user', None)
    return redirect(url_for('routes.homepage'))
