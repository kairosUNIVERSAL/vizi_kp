import sys
import os
from sqlalchemy import create_engine, text

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings

def test_connection():
    print(f"Testing connection to: {settings.DATABASE_URL.split('@')[-1]}") # Hide credentials
    
    url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
    
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"Connection successful: {result.scalar()}")
    except Exception as e:
        print(f"Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
