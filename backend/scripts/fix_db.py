import sys
import os
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def fix_database():
    print("Adding missing columns to database...")
    
    commands = [
        # User columns
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_tokens_used INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_api_cost NUMERIC(10, 4) DEFAULT 0",
        
        # Company columns
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS logo_path VARCHAR(500)",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS address VARCHAR(500) DEFAULT ''",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS website VARCHAR(255) DEFAULT ''",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS messenger_contact VARCHAR(100) DEFAULT ''",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS messenger_type VARCHAR(20) DEFAULT 'telegram'",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS inn VARCHAR(12) DEFAULT ''",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS kpp VARCHAR(9) DEFAULT ''",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS bank_name VARCHAR(255) DEFAULT ''",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS bank_account VARCHAR(20) DEFAULT ''",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS bank_bik VARCHAR(9) DEFAULT ''",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS bank_corr VARCHAR(20) DEFAULT ''"
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                print(f"  Executed: {cmd[:50]}...")
            except Exception as e:
                print(f"  Error (might already exist): {e}")
                
    print("Database fix complete.")

if __name__ == "__main__":
    fix_database()
