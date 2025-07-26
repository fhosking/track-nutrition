import streamlit as st
from streamlit_supabase_connect import get_supabase_client
from datetime import datetime

# Initialize Supabase client
@st.cache_resource
def get_db_client():
    return get_supabase_client()

sb = get_db_client()

# --- Database Functions ---
def fetch_brands():
    result = sb.table("brands").select("*").order("name", desc=False).execute()
    return result.data if result.data else []

def fetch_food_library():
    result = sb.table("food_library").select("*, brands(*)").order("name", desc=False).execute()
    return result.data if result.data else []

def add_brand(name):
    data = {"name": name}
    result = sb.table("brands").insert(data).execute()
    return result.data[0] if result.data else None

def add_food_to_library(name, carbs, protein, fat, alcohol, fibre, unit_type, serving_size, brand_id):
    data = {
        "name": name,
        "carbs_g": carbs,
        "protein_g": protein,
        "fat_g": fat,
        "alcohol_g": alcohol,
        "fibre_g": fibre,
        "unit_type": unit_type,
        "serving_size": serving_size,
        "brand_id": brand_id
    }
    result = sb.table("food_library").insert(data).execute()
    return result.data[0] if result.data else None

def fetch_food_log(date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    result = sb.table("food_log").select("*,food_library(*,brands(*))").eq("date", date).order("id", desc=False).execute()
    return result.data if result.data else []

def log_food_consumed(food_id, date, quantity):
    data = {"food_id": food_id, "date": date, "quantity": quantity}
    result = sb.table("food_log").insert(data).execute()
    return result.data[0] if result.data else None

def delete_food_log_entry(entry_id):
    result = sb.table("food_log").delete().eq("id", entry_id).execute()
    return result.data
