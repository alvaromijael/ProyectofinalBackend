from database.db import Base,engine
from models.User import AuthUser
from models.Patient import Patient
from models.Contact import Contact
from models.Appointment import Appointment
from models.Recipe import  Recipe
from models.Appointment import  AppointmentDiagnosis


Base.metadata.create_all(bind=engine)