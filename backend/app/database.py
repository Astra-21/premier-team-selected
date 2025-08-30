from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.engine import URL

url = URL.create(
    drivername="postgresql",   
    username=os.getenv("POSTGRES_USER", "myuser"),
    password=os.getenv("POSTGRES_PASSWORD", "mypass"),    
    host=os.getenv("DB_HOST", "db"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("POSTGRES_NAME", "mydb")
)

engine = create_engine(url, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
