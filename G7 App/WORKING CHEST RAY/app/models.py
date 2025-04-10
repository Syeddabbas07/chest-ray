from . import db
from enum import Enum
from datetime import datetime, timezone # To record timestamps for various actions
from sqlalchemy import UniqueConstraint

#values defined by using enum class for better readability and consistency
class AccessLevel(Enum):
    HEALTH_WORKER = 'health_worker'
    PATIENT = 'patient'
    EXPERT = 'expert'
    ADMIN = 'admin'

class HealthStatus(Enum):
    RED = "Critical"
    YELLOW = "Requires Attention"
    GREEN = "Stable"

class Priority(Enum):
    RED = "High"
    YELLOW = "Medium"
    GREEN = "Low"

class DosageFrequency(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

class Duration(Enum):
    DAYS = "Days"
    WEEKS = "Weeks"
    MONTHS = "Months"

class XrayPrediction(Enum):
    NORMAL = "NORMAL"
    PNEUMONIA = "PNEUMONIA"
    UNCLEAR = "UNCLEAR"


# WEBAPP USER TABLE 
# standard user when logged into the webapp and storing credentials for auth. this is the parent table for all other user types
# eg. patient, health worker, expert etc.
class WebAppUser(db.Model): 
    __tablename__ = 'app_user'

    uid = db.Column(db.Integer, primary_key=True)
    login_username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    access_level = db.Column(db.Enum(AccessLevel), nullable=False) # Access level of the user (patient, health worker, expert, admin)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships assigned to ensure that each user is added once by using uselist=False and establish a one to one relationship 
    # and since this is the parent user table backref=user is added to ensure an access from both sides
    patient_profile = db.relationship('Patient', back_populates='user', uselist=False)
    health_worker_profile = db.relationship('HealthWorker', back_populates='user', uselist=False)
    expert_profile = db.relationship('Expert', back_populates='user', uselist=False)
    admin_profile = db.relationship('Admin', back_populates='user', uselist=False)


# HEALTH WORKER TABLE
# created by admin to manage patients, register patients, upload xrays.
class HealthWorker(db.Model):
    __tablename__ = 'health_worker' 

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.uid'), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    appointed_country = db.Column(db.String(100), nullable=False)
    appointed_clinic = db.Column(db.String(100), nullable=False)
    contact_details = db.Column(db.String(200), nullable=False, unique=True)
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.HEALTH_WORKER)

    # Relationship this is a one to many relationship as a health worker can have multiple patients assigned to him/her
    # backpopulates allows patients to access their assigned health worker and lazy=True ensures that the data is loaded only when needed
    # this helps with performance and running queries
    user = db.relationship('WebAppUser', back_populates='health_worker_profile')
    patients = db.relationship('Patient', back_populates='assigned_health_worker')


# PATIENT TABLE
# self registered or can be done by health worker. only allowed to view their own data and xrays results and reports
class Patient(db.Model):
    __tablename__ = 'patient' 
    patient_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.uid'), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    address = db.Column(db.String(300))
    contact = db.Column(db.String(200))
    next_of_kin = db.Column(db.String(200))
    dob = db.Column(db.Date, nullable=False)  # Date of birth
    health_status = db.Column(db.Enum(HealthStatus), nullable=False)  # Similar to priority system
    clinician_id = db.Column(db.Integer, db.ForeignKey('health_worker.id'))
    next_of_kin_contact = db.Column(db.String(200), unique=True)
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.PATIENT)
    
    # Relationship this is a one to many relationship as a patient can have multiple xrays, treatments and reports
    user = db.relationship('WebAppUser', back_populates='patient_profile')
    assigned_health_worker = db.relationship('HealthWorker', back_populates='patients')
    treatments = db.relationship('Treatments', back_populates='patient')
    xrays = db.relationship('Xray', back_populates='patient')
    reports = db.relationship('Reports', back_populates='patient')


# TREATMENT TABLE
# treatments assigned by experts to patients after analysing the xray scans
class Treatments(db.Model):
    __tablename__ = 'treatment' 

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'), nullable=False)
    priority = db.Column(db.Enum(Priority), nullable=False)  # Treatment priority level according to enums defined above
    diagnosis_summary = db.Column(db.Text, nullable=False)   # summary of the analysis and treatments are assigned accordingly
    date_diagnosis = db.Column(db.DateTime, nullable=False)
    date_treatment_prescribed = db.Column(db.DateTime)
    prescribed_medications = db.Column(db.Text)
    duration = db.Column(db.Enum(Duration), nullable=True)  # Treatment duration for eg. 2 weeks, 3 months etc.
    dosage_frequency = db.Column(db.Enum(DosageFrequency), nullable=True)  # Medication schedule for eg. daily, weekly etc.

    #relationships assigned to ensure links to patients and experts
    patient = db.relationship('Patient', back_populates='treatments')
    expert = db.relationship('Expert', back_populates='treatments')

    # unique constraint to avoid duplicate treatments for the same patient
    __table_args__ = (UniqueConstraint('patient_id', 'expert_id', name='unique_treatment'),)


# X-RAY RECORDS TABLE
# xray scans uploaded by health workers for patients can be accessed by experts.
class Xray(db.Model): # table for x-ray records
    __tablename__ = 'xray_scans' 

    scan_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    health_worker_id = db.Column(db.Integer, db.ForeignKey('health_worker.id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'))
    image_path = db.Column(db.String(300), nullable=False) # path to the xray image to be stored in the server and identified.
    ml_prediction = db.Column(db.Enum(XrayPrediction), nullable=True, default=XrayPrediction.UNCLEAR)  # prediction of xray for eg. Pneumonia Detected, Normal, Unclear etc.
    status = db.Column(db.String(50), default="Pending") # status of the xray for eg. Pending, Reviewed, etc.
    date_uploaded = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))  # date the xray was uploaded 

    #relationships assigned to ensure links to patients, health workers and experts
    patient = db.relationship('Patient', back_populates='xrays')
    health_worker = db.relationship('HealthWorker')
    expert = db.relationship('Expert', back_populates='xrays', overlaps="expert")

    # unique constraint to avoid duplicate xrays for the same patient
    __table_args__ = (UniqueConstraint('patient_id', 'health_worker_id', name='unique_xray'),)


# REPORTS TABLE\
# reports generated by experts for patients after analysing the xray scans can be detailed analysis
class Reports(db.Model):  # table for storing generated reports
    __tablename__ = 'diagnostic_reports'  

    report_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.uid'), nullable=False)
    report_content = db.Column(db.Text, nullable=False)  # The content of the report in text
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # When the report was generated

    #relationships assigned to ensure links to patients and experts
    patient = db.relationship('Patient', back_populates='reports')
    expert = db.relationship('Expert', back_populates='reports')

    # unique constraint to avoid duplicate reports for the same patient
    __table_args__ = (UniqueConstraint('user_id', 'expert_id', name='unique_report'),)

    
# EXPERT TABLE
# created by admin and can view xrays, assign treatments to patients, generate reports analysing xrays etc.
class Expert(db.Model):
    __tablename__ = 'expert'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.uid'), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    contact_details = db.Column(db.String(200), nullable=False, unique=True)
    speciality = db.Column(db.String(150), nullable=False) # since its all chest xrays for pneumonia, the speciality is chest radiology
    country = db.Column(db.String(100), nullable=False)
    clinic = db.Column(db.String(100), nullable=False)
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.EXPERT)

    # Relationships assigned to ensure links to treatments, reports and xrays assigned to the expert
    user = db.relationship('WebAppUser', back_populates='expert_profile')
    treatments = db.relationship('Treatments', back_populates='expert')
    reports = db.relationship('Reports', back_populates='expert')
    xrays = db.relationship('Xray', back_populates='expert', overlaps="expert")

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.uid'), nullable=False, unique=True)
    contact_details = db.Column(db.String(200), nullable=False, unique=True)
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.ADMIN)

    # Relationships assigned to ensure links to Appuser.
    user = db.relationship('WebAppUser', back_populates='admin_profile')
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# END OF MODELS