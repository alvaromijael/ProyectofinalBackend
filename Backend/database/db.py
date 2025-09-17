from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


data="postgresql+psycopg2://admin:admin123@44.211.190.95:5432/fenixweb"
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(data, echo=True)
try:
    with engine.connect() as connection:
        print("Connected to database Postgress")
except Exception as e:
    print(f"An error ocurred: {e}")

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

