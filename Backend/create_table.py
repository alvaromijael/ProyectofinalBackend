from database.db import Base,engine
from models.User import AuthUser
from models.Patient import Patient
from models.Contact import Contact
from models.Appointment import Appointment


Base.metadata.create_all(bind=engine)