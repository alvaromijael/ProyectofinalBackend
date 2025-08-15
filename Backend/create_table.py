from database.db import Base,engine
from models.User import AuthUser

Base.metadata.create_all(bind=engine)