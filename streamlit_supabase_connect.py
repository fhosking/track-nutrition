import streamlit as st
from supabase import create_client, Client
import os

# DEBUG: Print secrets and environment variables
st.write("DEBUG: st.secrets SUPABASE_URL:", st.secrets.get("SUPABASE_URL", "NOT FOUND"))
st.write("DEBUG: st.secrets SUPABASE_KEY:", st.secrets.get("SUPABASE_KEY", "NOT FOUND"))
st.write("DEBUG: os.environ SUPABASE_URL:", os.getenv("SUPABASE_URL", "NOT FOUND"))
st.write("DEBUG: os.environ SUPABASE_KEY:", os.getenv("SUPABASE_KEY", "NOT FOUND"))

# Set your Supabase URL and anon key here or use Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] if "SUPABASE_KEY" in st.secrets else os.getenv("SUPABASE_KEY")

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Example usage: fetch all foods
def fetch_food_library():
    supabase = get_supabase_client()
    response = supabase.table("food_library").select("*").execute()
    return response.data

if __name__ == "__main__":
    st.write("Food Library:")
    foods = fetch_food_library()
    st.write(foods)
