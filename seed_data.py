"""
Seed the PostgreSQL database with sample interview data.
Run this after docker-compose is up and the database is ready.
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "username")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "interview_db")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def seed_database():
    """Create tables and populate with sample data."""
    
    engine = create_engine(DB_URL)
    
    # Drop existing tables if they exist (with CASCADE to handle foreign keys)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS user_history CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
    
    # Create tables
    with engine.connect() as conn:
        # Users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id INT UNIQUE NOT NULL,
                name VARCHAR(100),
                email VARCHAR(100),
                region VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Transactions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                transaction_id INT UNIQUE NOT NULL,
                user_id INT REFERENCES users(user_id),
                amount DECIMAL(10, 2),
                transaction_date TIMESTAMP,
                region VARCHAR(50)
            );
        """))
        
        # User history table (for deduplication exercises)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_history (
                id SERIAL PRIMARY KEY,
                user_id INT,
                email VARCHAR(100),
                updated_at TIMESTAMP
            );
        """))
        
        conn.commit()
    
    # Sample data
    users_data = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince', 'Eve Davis',
                 'Frank White', 'Grace Lee', 'Henry Harris', 'Iris Martinez', 'Jack Wilson'],
        'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'diana@example.com',
                  'eve@example.com', 'frank@example.com', 'grace@example.com', 'henry@example.com',
                  'iris@example.com', 'jack@example.com'],
        'region': ['North America', 'Europe', 'Asia', 'North America', 'Europe',
                   'Asia', 'South America', 'Africa', 'Oceania', 'North America']
    })
    
    # Generate transactions
    transactions_data = []
    for user_id in range(1, 11):
        for _ in range(random.randint(3, 8)):
            transaction_date = datetime.now() - timedelta(days=random.randint(1, 90))
            transactions_data.append({
                'transaction_id': len(transactions_data) + 1,
                'user_id': user_id,
                'amount': round(random.uniform(10, 5000), 2),
                'transaction_date': transaction_date,
                'region': users_data[users_data['user_id'] == user_id]['region'].values[0]
            })
    
    transactions_df = pd.DataFrame(transactions_data)
    
    # User history with duplicates (for deduplication exercise)
    user_history_data = []
    for user_id in range(1, 11):
        # Create 2-3 records per user with different emails and timestamps
        for i in range(random.randint(2, 3)):
            user_history_data.append({
                'user_id': user_id,
                'email': users_data[users_data['user_id'] == user_id]['email'].values[0] if i == 0 else f"alt_email_{user_id}_{i}@example.com",
                'updated_at': datetime.now() - timedelta(days=random.randint(1, 60))
            })
    
    user_history_df = pd.DataFrame(user_history_data)
    
    # Insert data into database - users first, then transactions (which has FK to users)
    users_data.to_sql('users', engine, if_exists='append', index=False)
    transactions_df.to_sql('transactions', engine, if_exists='append', index=False)
    user_history_df.to_sql('user_history', engine, if_exists='append', index=False)
    
    print("✅ Database seeded successfully!")
    print(f"   - {len(users_data)} users")
    print(f"   - {len(transactions_df)} transactions")
    print(f"   - {len(user_history_df)} user history records")

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
