import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path to import database functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import fetch_food_log, delete_food_log_entry

st.set_page_config(page_title="Today's Food Log", layout="centered")
st.title("📊 Today's Food Log")

# --- Main UI ---
today = datetime.now().strftime("%Y-%m-%d")

# Initialize session state for date navigation
if 'display_date' not in st.session_state:
    st.session_state.display_date = today

# Date navigation
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("← Previous Day"):
        current_date = datetime.strptime(st.session_state.display_date, "%Y-%m-%d")
        prev_date = current_date - pd.Timedelta(days=1)
        st.session_state.display_date = prev_date.strftime("%Y-%m-%d")
        st.rerun()

with col2:
    display_date_formatted = datetime.strptime(st.session_state.display_date, "%Y-%m-%d").strftime("%A, %B %d, %Y")
    if st.session_state.display_date == today:
        st.subheader(f"Today's Food Log ({display_date_formatted})")
    else:
        st.subheader(f"Food Log for {display_date_formatted}")

with col3:
    if st.button("Next Day →"):
        current_date = datetime.strptime(st.session_state.display_date, "%Y-%m-%d")
        next_date = current_date + pd.Timedelta(days=1)
        st.session_state.display_date = next_date.strftime("%Y-%m-%d")
        st.rerun()

# Return to today button
if st.session_state.display_date != today:
    if st.button("Return to Today"):
        st.session_state.display_date = today
        st.rerun()

# Fetch and display food log for the selected date
food_log = fetch_food_log(st.session_state.display_date)

if food_log:
    df_log = pd.DataFrame(food_log)
    # Expand food_library fields
    if "food_library" in df_log.columns:
        lib_df = pd.json_normalize(df_log["food_library"])
        for col in ["name", "carbs_g", "protein_g", "fat_g", "alcohol_g", "fibre_g", "unit_type"]:
            if col in lib_df.columns:
                df_log[col] = lib_df[col]
        
        # Handle brand information from nested structure
        brand_names = []
        for food_data in df_log["food_library"]:
            if food_data and isinstance(food_data, dict):
                brands_data = food_data.get("brands")
                if brands_data and isinstance(brands_data, dict):
                    brand_names.append(brands_data.get("name", "No brand"))
                else:
                    brand_names.append("No brand")
            else:
                brand_names.append("No brand")
        df_log["brand_name"] = brand_names
    
    # Calculate macros per entry based on unit_type and compute calories
    for idx, row in df_log.iterrows():
        unit_type = row.get("unit_type", "unit")
        quantity = row["quantity"]
        if unit_type == "unit":
            factor = quantity
        elif unit_type == "weight (g)":
            factor = quantity / 100.0
        else:
            # Default to unit if unit_type is unclear
            factor = quantity
        
        debug_macros = {}
        for macro in ["carbs_g", "protein_g", "fat_g", "alcohol_g", "fibre_g"]:
            debug_macros[macro] = float(row.get(macro, 0)) * factor
            df_log.at[idx, macro] = debug_macros[macro]
        
        calories = (
            debug_macros["carbs_g"] * 4 +
            debug_macros["protein_g"] * 4 +
            debug_macros["fat_g"] * 9 +
            debug_macros["alcohol_g"] * 7
        )
        df_log.at[idx, "calories"] = calories

    # Display entries with delete buttons
    st.subheader("Entries:")
    for idx, row in df_log.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1:
            unit_display = "g" if row.get('unit_type') == "weight (g)" else "units"
            st.write(f"**{row['name']}** ({row.get('brand_name', 'No brand')}) - {row['quantity']} {unit_display}")
            st.write(f"Calories: {row['calories']:.0f} | Carbs: {row['carbs_g']:.1f}g | Protein: {row['protein_g']:.1f}g | Fat: {row['fat_g']:.1f}g | Fibre: {row['fibre_g']:.1f}g")
            # Debug info
            if st.checkbox(f"Debug info for {row['name']}", key=f"debug_{row['id']}"):
                st.write(f"Unit type: {row.get('unit_type')}")
                st.write(f"Raw food_library data: {row.get('food_library')}")
        with col2:
            if st.button(f"🗑️ Delete", key=f"delete_{row['id']}"):
                delete_food_log_entry(row["id"])
                st.success("Entry deleted!")
                st.rerun()
        st.markdown("---")
    
    # Daily totals
    totals = {macro: df_log[macro].sum() for macro in ["carbs_g", "protein_g", "fat_g", "alcohol_g", "fibre_g", "calories"]}
    st.markdown(f"**Daily Totals:**")
    st.markdown(
        f"Calories: {totals['calories']:.0f} kcal | Carbs: {totals['carbs_g']:.1f}g | Protein: {totals['protein_g']:.1f}g | Fat: {totals['fat_g']:.1f}g | Fibre: {totals['fibre_g']:.1f}g | Alcohol: {totals['alcohol_g']:.1f}g"
    )
else:
    st.info(f"No foods logged for {display_date_formatted} yet.")
    st.info("👈 Use the main page to add foods to your log!")
