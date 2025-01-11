from sqlmodel import create_engine, SQLModel

# Database URL - simple local SQLite database
DATABASE_URL = "sqlite:///mirror.db"

# Create engine
# echo=True means SQL statements will be logged
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables() -> None:
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)