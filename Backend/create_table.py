from database.db import Base,engine
from models.User import AuthUser
from models.Patient import Paciente
Base.metadata.create_all(bind=engine)