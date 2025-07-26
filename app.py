import streamlit as st
from datetime import datetime
from llm_assistant import show_llm_assistant
from database import (
    fetch_brands, fetch_food_library, add_brand, add_food_to_library, 
    log_food_consumed, fetch_food_log
)

st.set_page_config(page_title="Food Log - Add Food", layout="centered")
st.title("🍽️ Food Log Tracker")

st.markdown("---")

# --- Main UI ---
today = datetime.now().strftime("%Y-%m-%d")

# Initialize session state for date navigation
if 'display_date' not in st.session_state:
    st.session_state.display_date = today

# --- Food Entry Section ---
st.subheader("Log Food or Drink Consumed")

# Date selection for logging
log_date = st.date_input("Date to log food for:", value=datetime.now().date())
log_date_str = log_date.strftime("%Y-%m-%d")

# --- LLM Assistant Section ---
show_llm_assistant()

st.markdown("---")

brands = fetch_brands()
food_library = fetch_food_library()

# Step 1: Brand selection
# Custom brand ordering: Homemade and Generic first, then rest alphabetical
homemade = next((b["name"] for b in brands if b["name"].lower() == "homemade meal"), None)
generic = next((b["name"] for b in brands if b["name"].lower() == "generic food"), None)
other_brands = sorted([b["name"] for b in brands if b["name"].lower() not in ["homemade meal", "generic food"]])
brand_options = ["Create new brand..."]
if homemade:
    brand_options.append(homemade)
if generic:
    brand_options.append(generic)
brand_options += other_brands
selected_brand_name = st.selectbox("Step 1: Select brand", brand_options)

# Handle brand creation
if selected_brand_name == "Create new brand...":
    with st.form("create_brand_form"):
        new_brand_name = st.text_input("Enter new brand name")
        submitted = st.form_submit_button("Create Brand")
        if submitted and new_brand_name:
            new_brand = add_brand(new_brand_name)
            if new_brand:
                st.success(f"Created brand '{new_brand_name}'")
                st.rerun()
        elif submitted:
            st.error("Please enter a brand name.")
    st.stop()  # Stop here until brand is created

# Get selected brand ID
selected_brand = next((b for b in brands if b["name"] == selected_brand_name), None)
if not selected_brand:
    st.error("Selected brand not found.")
    st.stop()

# Step 2: Food selection (only enabled after brand selection)
st.write(f"Selected brand: **{selected_brand_name}**")

# Filter foods by selected brand
filtered_foods = [f for f in food_library if f.get('brand_id') == selected_brand['id']]
if filtered_foods:
    food_options = ["Add new item..."] + [f["name"] for f in filtered_foods]
    food_choice = st.selectbox("Step 2: Select item", food_options)
else:
    st.info(f"No items found for brand '{selected_brand_name}'. Add a new item below.")
    food_options = ["Add new item..."]
    food_choice = st.selectbox("Step 2: Select item", food_options)

if food_choice == "Add new item...":
    st.info(f"Add a new food or drink to your library for brand '{selected_brand_name}' and log it as consumed.")
    
    # Unit type selection outside form for dynamic updates
    unit_type = st.selectbox("How is this item measured?", ["unit", "weight (g)"], key="unit_type_select")
    
    with st.form("add_food_form"):
        name = st.text_input("Name (e.g. Chicken Breast, Beer)")
        st.write(f"Brand: **{selected_brand_name}**")
        st.write(f"Measurement type: **{unit_type}**")
        
        # Dynamic serving size and labels based on unit type
        if unit_type == "weight (g)":
            serving_size = st.text_input("Serving size (reference)", value="100g", disabled=True)
            carbs = st.number_input("Carbs per 100g/100ml", min_value=0.0, value=0.0)
            protein = st.number_input("Protein per 100g/100ml", min_value=0.0, value=0.0)
            fat = st.number_input("Fat per 100g/100ml", min_value=0.0, value=0.0)
            fibre = st.number_input("Fibre per 100g/100ml", min_value=0.0, value=0.0)
            alcohol = st.number_input("Alcohol per 100g/100ml", min_value=0.0, value=0.0)
            quantity = st.number_input("How many grams did you consume?", min_value=0.0, value=0.0)
        else:
            serving_size = st.text_input("Serving size (e.g. 1 apple, 1 can, 1 slice)")
            carbs = st.number_input("Carbs per unit", min_value=0.0, value=0.0)
            protein = st.number_input("Protein per unit", min_value=0.0, value=0.0)
            fat = st.number_input("Fat per unit", min_value=0.0, value=0.0)
            fibre = st.number_input("Fibre per unit", min_value=0.0, value=0.0)
            alcohol = st.number_input("Alcohol per unit", min_value=0.0, value=0.0)
            quantity = st.number_input("How many units did you consume?", min_value=0.0, value=1.0)
        
        submitted = st.form_submit_button("Add and Log")
        if submitted and name:
            if quantity == 0:
                st.warning("Quantity cannot be zero.")
            else:
                new_food = add_food_to_library(name, carbs, protein, fat, alcohol, fibre, unit_type, serving_size, selected_brand['id'])
                if new_food:
                    log_food_consumed(new_food["id"], log_date_str, quantity)
                    st.success(f"Added '{name}' and logged as consumed on {log_date_str}.")
                    st.rerun()
        elif submitted:
            st.error("Please enter a name for the food or drink.")
elif food_choice and food_choice != "Add new item...":
    # Find the selected food by name and brand
    selected_food = next((f for f in filtered_foods if f["name"] == food_choice), None)
    if selected_food:
        with st.form("log_existing_food_form"):
            if selected_food.get("unit_type", "unit") == "unit":
                quantity = st.number_input(f"How many units of '{food_choice}' did you consume?", min_value=0.0, value=1.0)
            else:
                quantity = st.number_input(f"How many grams of '{food_choice}' did you consume? (per 100g macros)", min_value=0.0, value=0.0)
            submitted = st.form_submit_button("Log Consumption")
            if submitted:
                if quantity == 0:
                    st.warning("Quantity cannot be zero.")
                else:
                    log_food_consumed(selected_food["id"], log_date_str, quantity)
                    st.success(f"Logged {quantity} of '{food_choice}' for {log_date_str}.")
                    st.rerun()


