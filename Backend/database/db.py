from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

data="postgresql+psycopg2://admin:admin123@localhost:5432/fenixweb"
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
try:
    with engine.connect() as connection:
        print("Connected to database Postgress")
except Exception as e:
    print(f"An error ocurred: {e}")

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False)
