import re
import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai
import bcrypt

# ------ Secrets ------
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
HASHED_PASSWORD = st.secrets["HASHED_PASSWORD"].encode("utf-8")

# ------ Database URL builder ------
def get_db_url():
    user = st.secrets["POSTGRES_USERNAME"]
    password = st.secrets["POSTGRES_PASSWORD"]
    host = st.secrets["POSTGRES_HOST"]
    port = st.secrets["POSTGRES_PORT"]
    db = st.secrets["POSTGRES_DATABASE"]
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

# Database Schema (context for AI)
DATABASE_SCHEMA = """
Database Schema:

LOOKUP TABLES:
- ProductCategory(ProductCategoryID, ProductCategory, ProductCategoryDescription)

CORE TABLES:
- Region(RegionID, Region)
- Country(CountryID, Country, RegionID)
- Customer(CustomerID, FirstName, LastName, Address, City, CountryID)
- Product(ProductID, ProductName, ProductUnitPrice, ProductCategoryID)
- OrderDetail(OrderID, CustomerID, ProductID, OrderDate, QuantityOrdered)
"""

# ------ Login ------
def login_screen():
    st.title("🔐 Secure Login")
    password = st.text_input("Enter password:", type="password")

    if st.button("Login"):
        if bcrypt.checkpw(password.encode("utf-8"), HASHED_PASSWORD):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password ❌")


def require_login():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_screen()
        st.stop()

# ------ Database Handler ------
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(get_db_url())
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


def run_query(sql):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        return pd.read_sql_query(sql, conn)
    except Exception as e:
        st.error(f"Query Error: {e}")
        return None

# ------ Gemini SQL Generator ------
@st.cache_resource
def get_openai_client():
    genai.configure(api_key=OPENAI_API_KEY)
    return genai.GenerativeModel("models/gemini-2.5-flash")


def extract_sql(response_text):
    return re.sub(r"```sql|```", "", response_text).strip()


def generate_sql(question):
    model = get_openai_client()
    prompt = f"""
You are a PostgreSQL expert. Return ONLY SQL query.

Schema:
{DATABASE_SCHEMA}

Question:
{question}
"""
    try:
        response = model.generate_content(prompt)
        return extract_sql(response.text)
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None


# ------ UI ------
def main():
    require_login()

    st.title("🤖 AI-Powered SQL Query Assistant")
    question = st.text_area("Ask a question:")

    if st.button("Generate SQL"):
        if question.strip():
            with st.spinner("Generating SQL..."):
                sql = generate_sql(question)
                if sql:
                    st.code(sql, language="sql")
                    if st.button("Run Query"):
                        df = run_query(sql)
                        if df is not None:
                            st.dataframe(df)

if __name__ == "__main__":
    main()

