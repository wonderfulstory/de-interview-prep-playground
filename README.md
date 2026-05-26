# 🚀 Data Engineering Interview Playground

A full-stack SQL + Python interview practice environment with PostgreSQL backend, Streamlit frontend, and automated accuracy testing.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Streamlit Web UI (SQL + Python + Testing)      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Python Backend (psycopg2 + SQLAlchemy)         │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  PostgreSQL Database (Docker)                    │
└─────────────────────────────────────────────────┘
```

## Quick Start

### 1. Set up environment variables
```bash
cp .env.example .env
```

### 2. Start PostgreSQL with Docker
```bash
docker-compose up -d
```

Wait for the database to be healthy:
```bash
docker-compose ps
```

### 3. Seed the database with sample data
```bash
python seed_data.py
```

You should see:
```
✅ Database seeded successfully!
   - 10 users
   - 56 transactions
   - 25 user history records
```

### 4. Run the Streamlit app
```bash
streamlit run playground.py
```

The app will open at `http://localhost:8501`

---

## Features

### 📊 SQL Editor
- Write and execute SQL queries directly against PostgreSQL
- View results as formatted DataFrames
- Pass query results to Python for transformation

**Example:**
```sql
SELECT user_id, SUM(amount) as total_spent 
FROM transactions 
GROUP BY user_id 
ORDER BY total_spent DESC 
LIMIT 5;
```

### 🐍 Python Editor
- Transform data using pandas and Python
- Automatically access SQL query results via the `df` variable
- Execute any Python code with access to pandas, numpy, etc.

**Example:**
```python
import pandas as pd

# df is available from your SQL query
result = df.groupby('region').agg({
    'amount': ['sum', 'mean', 'count']
}).round(2)
```

### 🧪 Accuracy Tests
- Test SQL and Python solutions against expected outputs
- Column validation
- Row-level comparison
- Pre-built interview questions

**Test Cases Included:**
1. **Q1: Total Revenue by Region** - Aggregation with JOIN
2. **Q2: Deduplicate Users** - Window functions & deduplication
3. **Q3: Top 3 Spenders Per Month** - Advanced grouping

---

## Database Schema

### `users` table
```sql
id (PK)  | user_id | name         | email              | region          | created_at
---------|---------|--------------|-------------------|-----------------|----------
1        | 1       | Alice Johnson| alice@example.com | North America   | 2024-01-15
2        | 2       | Bob Smith    | bob@example.com   | Europe          | 2024-01-16
...
```

### `transactions` table
```sql
id (PK) | transaction_id | user_id | amount   | transaction_date      | region
--------|----------------|---------|----------|---------------------|----------
1       | 1              | 1       | 150.50   | 2024-05-10 10:30:00 | North America
2       | 2              | 2       | 2500.00  | 2024-05-11 14:20:00 | Europe
...
```

### `user_history` table (for deduplication exercises)
```sql
id (PK) | user_id | email                | updated_at
--------|---------|---------------------|------------------
1       | 1       | alice@example.com    | 2024-05-20 09:00:00
2       | 1       | old_alice@example.com| 2024-04-15 15:30:00
...
```

---

## Recommended Interview Practice Path

### Level 1: SQL Basics
- **Query all users by region**
  ```sql
  SELECT region, COUNT(*) as user_count 
  FROM users 
  GROUP BY region;
  ```

- **Find total spending per user**
  ```sql
  SELECT user_id, SUM(amount) as total_spent 
  FROM transactions 
  GROUP BY user_id;
  ```

### Level 2: Advanced SQL
- **Window Functions: Rank top spenders**
  ```sql
  SELECT 
    user_id, 
    amount,
    RANK() OVER (ORDER BY amount DESC) as rank
  FROM transactions
  LIMIT 10;
  ```

- **Deduplication with DISTINCT ON**
  ```sql
  SELECT DISTINCT ON (user_id) user_id, email, updated_at 
  FROM user_history 
  ORDER BY user_id, updated_at DESC;
  ```

### Level 3: Python ETL
- **Data Cleaning**
  ```python
  # Remove nulls, standardize formats
  df_clean = df.dropna(subset=['email'])
  df_clean['email'] = df_clean['email'].str.lower()
  ```

- **Feature Engineering**
  ```python
  df['spending_tier'] = pd.cut(df['amount'], bins=[0, 100, 500, 5000], 
                                labels=['low', 'medium', 'high'])
  ```

### Level 4: SQL + Python (ETL Pipeline)
1. Extract last 7 days of transactions
2. Calculate tax by region
3. Generate summary report as JSON

---

## File Structure

```
de-interview-prep-playground/
├── playground.py              # Main Streamlit app
├── seed_data.py              # Database initialization script
├── docker-compose.yml        # PostgreSQL Docker config
├── .env.example              # Environment variables template
├── .env                      # Your local env (git-ignored)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Troubleshooting

### ❌ "Cannot connect to PostgreSQL"
```bash
# Check if Docker container is running
docker-compose ps

# Restart if needed
docker-compose restart

# Check logs
docker-compose logs postgres
```

### ❌ "psycopg2.OperationalError: password authentication failed"
- Make sure `.env` matches `docker-compose.yml`
- Default: `username` / `password`

### ❌ "Table does not exist"
```bash
# Re-seed the database
python seed_data.py
```

### ❌ Streamlit app won't start
```bash
# Make sure .env file exists in the root directory
cp .env.example .env

# Check Python environment
which python

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Advanced Setup: Jupyter Notebook Alternative

If you prefer notebooks over Streamlit, use `ipython-sql`:

```bash
pip install jupyter ipython-sql
```

Create a notebook and use:
```python
%load_ext sql
%sql postgresql://username:password@localhost:5432/interview_db

%%sql
SELECT * FROM users LIMIT 5;
```

---

## Next Steps

- 📚 Add more complex test cases
- 🔒 Add solution validation logic
- 📊 Build a dashboard with execution history
- 🚀 Deploy to a cloud provider (Heroku, AWS, etc.)

---

## Requirements

- Python 3.8+
- Docker & Docker Compose
- PostgreSQL (via Docker)
- Dependencies: See `requirements.txt`

---

**Happy practicing! 🎯**
