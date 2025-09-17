from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Connection string format:
# "mysql+mysqlconnector://username:password@host/database_name"
DATABASE_URL = "mysql+mysqlconnector://pizza_user:Noahjanssen9@localhost/pizza_db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True prints SQL queries

# Base class for ORM models
Base = declarative_base()

# Session factory
Session = sessionmaker(bind=engine)
