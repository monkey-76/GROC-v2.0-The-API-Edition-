from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

db_pwd=os.getenv("DB_PWD")

DB_URL=f"postgresql://admin:{db_pwd}@localhost:5432/admin"#postgresql://user:your_password@localhost:5432/admin"

engine = create_engine(DB_URL)
SessionLocal =sessionmaker(autocommit=False, autoflush=False, bind=engine)