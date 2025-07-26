import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import database functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import fetch_food_library

st.set_page_config(page_title="Food & Drink Library", layout="wide")
st.title("📚 Food & Drink Library")

st.info("Browse all foods and drinks in your library. Use the main page to add new items!")

# Fetch and display food library
food_library = fetch_food_library()

if food_library:
    df_lib = pd.DataFrame(food_library)
    
    # Extract brand names from nested brands object
    if "brands" in df_lib.columns:
        brand_names = []
        for brands_data in df_lib["brands"]:
            if brands_data and isinstance(brands_data, dict):
                brand_names.append(brands_data.get("name", "No brand"))
            else:
                brand_names.append("No brand")
        df_lib["brand_name"] = brand_names
        display_cols = ["name", "brand_name", "serving_size", "unit_type", "carbs_g", "protein_g", "fat_g", "fibre_g", "alcohol_g"]
    else:
        display_cols = ["name", "serving_size", "unit_type", "carbs_g", "protein_g", "fat_g", "fibre_g", "alcohol_g"]
    
    # Add search functionality
    st.subheader("🔍 Search & Filter")
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("Search by food name:", placeholder="e.g., chicken, pasta, apple")
    
    with col2:
        if "brand_name" in df_lib.columns:
            unique_brands = ["All brands"] + sorted(df_lib["brand_name"].unique().tolist())
            selected_brand = st.selectbox("Filter by brand:", unique_brands)
        else:
            selected_brand = "All brands"
    
    # Apply filters
    filtered_df = df_lib.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df["name"].str.contains(search_term, case=False, na=False)]
    
    if selected_brand != "All brands":
        filtered_df = filtered_df[filtered_df["brand_name"] == selected_brand]
    
    # Display results
    st.subheader(f"📋 Library ({len(filtered_df)} items)")
    
    if not filtered_df.empty:
        # Sort by name for better browsing
        filtered_df = filtered_df.sort_values("name")
        
        # Display as a nice table
        st.dataframe(
            filtered_df[display_cols], 
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": st.column_config.TextColumn("Food/Drink Name", width="medium"),
                "brand_name": st.column_config.TextColumn("Brand", width="small"),
                "serving_size": st.column_config.TextColumn("Serving Size", width="small"),
                "unit_type": st.column_config.TextColumn("Unit Type", width="small"),
                "carbs_g": st.column_config.NumberColumn("Carbs (g)", format="%.1f"),
                "protein_g": st.column_config.NumberColumn("Protein (g)", format="%.1f"),
                "fat_g": st.column_config.NumberColumn("Fat (g)", format="%.1f"),
                "fibre_g": st.column_config.NumberColumn("Fibre (g)", format="%.1f"),
                "alcohol_g": st.column_config.NumberColumn("Alcohol (g)", format="%.1f"),
            }
        )
        
        # Summary statistics
        st.subheader("📊 Library Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_items = len(filtered_df)
            st.metric("Total Items", total_items)
        
        with col2:
            unit_items = len(filtered_df[filtered_df["unit_type"] == "unit"])
            st.metric("Unit-based Items", unit_items)
        
        with col3:
            weight_items = len(filtered_df[filtered_df["unit_type"] == "weight (g)"])
            st.metric("Weight-based Items", weight_items)
        
        with col4:
            if "brand_name" in filtered_df.columns:
                unique_brands_count = filtered_df["brand_name"].nunique()
                st.metric("Unique Brands", unique_brands_count)
    else:
        st.info("No items match your search criteria. Try adjusting your filters.")
        
else:
    st.info("Your food and drink library is empty. Add new items using the main page!")
    
st.markdown("---")
st.markdown("💡 **Tip:** Use the main page to add new foods and drinks to your library.")
