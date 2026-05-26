import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="Data Engineering Interview Playground", layout="wide")

# Database connection configuration
DB_USER = os.getenv("DB_USER", "username")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "interview_db")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize session state
if 'last_sql_result' not in st.session_state:
    st.session_state['last_sql_result'] = pd.DataFrame()
if 'last_python_result' not in st.session_state:
    st.session_state['last_python_result'] = None
if 'refresh_tables' not in st.session_state:
    st.session_state['refresh_tables'] = False

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_all_tables():
    """Get list of all tables in the database."""
    try:
        engine = create_engine(DB_URL)
        inspector = inspect(engine)
        return sorted(inspector.get_table_names())
    except Exception as e:
        st.error(f"Error fetching tables: {e}")
        return []

def get_table_schema(table_name):
    """Get column schema for a table."""
    try:
        engine = create_engine(DB_URL)
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return columns
    except Exception as e:
        return []

def get_table_row_count(table_name):
    """Get row count for a table."""
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
    except Exception as e:
        return 0

def create_table(table_name, create_sql):
    """Create a new table."""
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text(create_sql))
            conn.commit()
        st.success(f"✅ Table '{table_name}' created successfully!")
        st.session_state['refresh_tables'] = True
        return True
    except Exception as e:
        st.error(f"❌ Error creating table: {e}")
        return False

def drop_table(table_name):
    """Drop a table."""
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
            conn.commit()
        st.success(f"✅ Table '{table_name}' dropped successfully!")
        st.session_state['refresh_tables'] = True
        return True
    except Exception as e:
        st.error(f"❌ Error dropping table: {e}")
        return False

# ============================================
# SIDEBAR: TABLE MANAGEMENT
# ============================================
with st.sidebar:
    st.header("📊 Database Tables")
    
    tables = get_all_tables()
    
    if tables:
        st.subheader(f"Tables ({len(tables)})")
        
        # Display each table with options
        for table_name in tables:
            with st.expander(f"📋 {table_name}"):
                row_count = get_table_row_count(table_name)
                st.write(f"**Rows:** {row_count}")
                
                # Show schema
                st.write("**Schema:**")
                columns = get_table_schema(table_name)
                for col in columns:
                    col_type = str(col['type'])
                    st.caption(f"- `{col['name']}`: {col_type}")
                
                # Preview data
                if st.button(f"👁️ Preview {table_name}", key=f"preview_{table_name}"):
                    try:
                        engine = create_engine(DB_URL)
                        preview_df = pd.read_sql(text(f"SELECT * FROM {table_name} LIMIT 5"), engine)
                        st.dataframe(preview_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error previewing: {e}")
                
                # Drop table button
                if st.button(f"🗑️ Drop {table_name}", key=f"drop_{table_name}"):
                    if drop_table(table_name):
                        st.rerun()
    else:
        st.info("No tables found in database.")
    
    st.divider()
    
    # Create new table section
    st.subheader("➕ Create New Table")
    create_table_name = st.text_input("Table name:", placeholder="my_table")
    
    create_sql_template = """CREATE TABLE IF NOT EXISTS table_name (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""
    
    create_sql = st.text_area(
        "SQL CREATE statement:",
        value=create_sql_template,
        height=150,
        key="create_table_sql"
    )
    
    if st.button("✅ Create Table"):
        if create_table_name and create_sql:
            # Replace placeholder with actual table name
            sql_with_name = create_sql.replace("table_name", create_table_name)
            if create_table(create_table_name, sql_with_name):
                st.rerun()
        else:
            st.error("Please enter table name and SQL!")

st.title("🚀 Data Engineering Interview Playground")
st.markdown("**SQL Editor** | **Python Transformer** | **Accuracy Testing**")

# Create tabs
tab1, tab2, tab3 = st.tabs(["SQL Editor", "Python Editor", "Accuracy Tests"])

# ============================================
# TAB 1: SQL EDITOR
# ============================================
with tab1:
    st.subheader("PostgreSQL Interface")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        with st.form("sql_form"):
            sql_input = st.text_area(
                "Write your SQL query here (Cmd/Ctrl + Enter to run):",
                height=250,
                value="SELECT * FROM users LIMIT 5;",
                key="sql_input"
            )
            execute_sql_btn = st.form_submit_button("▶️ Execute SQL")
    
    with col2:
        st.markdown("### Sample Queries")
        if st.button("📊 Show Users"):
            st.session_state['sql_input'] = "SELECT * FROM users LIMIT 5;"
            st.rerun()
        if st.button("📈 Top Revenue"):
            st.session_state['sql_input'] = "SELECT user_id, SUM(amount) as total FROM transactions GROUP BY user_id ORDER BY total DESC LIMIT 5;"
            st.rerun()
    
    if execute_sql_btn:
        try:
            engine = create_engine(DB_URL)
            with engine.connect() as conn:
                df = pd.read_sql(text(sql_input), conn)
                st.session_state['last_sql_result'] = df
                st.success(f"✅ Query executed. Rows returned: {len(df)}")
                st.dataframe(df, width="stretch")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# ============================================
# TAB 2: PYTHON EDITOR
# ============================================
with tab2:
    st.subheader("Python Data Transformation")
    
    with st.form("python_form"):
        python_input = st.text_area(
            "Write Python (use 'df' to refer to your last SQL result). Cmd/Ctrl + Enter to run:",
            height=300,
            value="""import pandas as pd
# Transform the SQL result
result = df.groupby('user_id').agg({
    'amount': 'sum',
    'transaction_date': 'count'
}).rename(columns={'transaction_date': 'num_transactions'})
result = result.sort_values('amount', ascending=False)""",
            key="python_input"
        )
        execute_py_btn = st.form_submit_button("▶️ Run Python")
        
    if execute_py_btn:
        try:
            df = st.session_state.get('last_sql_result', pd.DataFrame())
            
            if df.empty:
                st.warning("⚠️ No SQL result available. Run a SQL query first!")
            else:
                # Execute the Python code
                local_vars = {'df': df, 'pd': pd}
                exec(python_input, {}, local_vars)
                
                st.session_state['last_python_result'] = local_vars.get('result')
                
                st.success("✅ Python code executed!")
                result = local_vars.get('result')
                
                if result is not None:
                    st.write("**Output:**")
                    if isinstance(result, pd.DataFrame):
                        st.dataframe(result, width="stretch")
                    else:
                        st.write(result)
                else:
                    st.info("ℹ️ No 'result' variable defined. Check your code.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# ============================================
# TAB 3: ACCURACY TESTS
# ============================================
with tab3:
    st.subheader("🧪 Accuracy Testing")
    
    # Define test cases
    test_cases = {
        "Q1: Total Revenue by Region": {
            "sql": "SELECT region, SUM(amount) as total_revenue FROM transactions JOIN users ON transactions.user_id = users.id GROUP BY region ORDER BY total_revenue DESC;",
            "expected_columns": ["region", "total_revenue"]
        },
        "Q2: Deduplicate Users": {
            "sql": "SELECT DISTINCT ON (user_id) user_id, email, updated_at FROM user_history ORDER BY user_id, updated_at DESC;",
            "expected_columns": ["user_id", "email", "updated_at"]
        },
        "Q3: Top 3 Spenders Per Month": {
            "sql": "SELECT EXTRACT(YEAR_MONTH FROM transaction_date) as month, user_id, SUM(amount) as total FROM transactions GROUP BY month, user_id ORDER BY month, total DESC;",
            "expected_columns": ["month", "user_id", "total"]
        }
    }
    
    test_question = st.selectbox("📝 Select a Test Question:", list(test_cases.keys()))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Your Solution:**")
        with st.form("test_form"):
            user_solution = st.text_area(
                "Write your SQL or Python solution (Cmd/Ctrl + Enter to run):",
                height=200,
                key="test_solution"
            )
            run_test_btn = st.form_submit_button("🔍 Run Test")
    
    with col2:
        st.write("**Expected Output Format:**")
        expected_cols = test_cases[test_question]["expected_columns"]
        st.code(f"Columns: {', '.join(expected_cols)}", language="text")
    
    if run_test_btn:
        try:
            engine = create_engine(DB_URL)
            with engine.connect() as conn:
                user_df = pd.read_sql(text(user_solution), conn)
            
            # Check columns match
            expected_cols = test_cases[test_question]["expected_columns"]
            user_cols = list(user_df.columns)
            
            if set(user_cols) == set(expected_cols):
                st.success("✅ **PASS** - Column names match expected output!")
                st.dataframe(user_df, width="stretch")
            else:
                st.error(f"❌ **FAIL** - Column mismatch")
                st.write(f"Expected: {expected_cols}")
                st.write(f"Got: {user_cols}")
                st.dataframe(user_df, width="stretch")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.divider()
st.markdown("**💡 Tip:** Run SQL first, then use the result in the Python editor with the `df` variable.")
