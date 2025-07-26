import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import database functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import fetch_food_log

st.set_page_config(page_title="Nutrition Graph", layout="wide")
st.title("📈 Nutrition Trends")

# Date range selector
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
with col2:
    end_date = st.date_input("End Date", value=datetime.now())

if start_date <= end_date:
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Collect data for each date
    daily_data = []
    for date in date_range:
        date_str = date.strftime("%Y-%m-%d")
        food_log = fetch_food_log(date_str)
        
        if food_log:
            df_log = pd.DataFrame(food_log)
            # Process the data similar to the food log page
            if "food_library" in df_log.columns:
                lib_df = pd.json_normalize(df_log["food_library"])
                for col in ["name", "carbs_g", "protein_g", "fat_g", "alcohol_g", "fibre_g", "unit_type"]:
                    if col in lib_df.columns:
                        df_log[col] = lib_df[col]
                
                # Calculate macros per entry
                for idx, row in df_log.iterrows():
                    unit_type = row.get("unit_type", "unit")
                    quantity = row["quantity"]
                    if unit_type == "unit":
                        factor = quantity
                    elif unit_type == "weight (g)":
                        factor = quantity / 100.0
                    else:
                        factor = quantity
                    
                    for macro in ["carbs_g", "protein_g", "fat_g", "alcohol_g", "fibre_g"]:
                        df_log.at[idx, macro] = float(row.get(macro, 0)) * factor
                    
                    calories = (
                        df_log.at[idx, "carbs_g"] * 4 +
                        df_log.at[idx, "protein_g"] * 4 +
                        df_log.at[idx, "fat_g"] * 9 +
                        df_log.at[idx, "alcohol_g"] * 7
                    )
                    df_log.at[idx, "calories"] = calories
                
                # Sum totals for the day
                daily_totals = {
                    "date": date_str,
                    "calories": df_log["calories"].sum(),
                    "carbs_g": df_log["carbs_g"].sum(),
                    "protein_g": df_log["protein_g"].sum(),
                    "fat_g": df_log["fat_g"].sum(),
                    "fibre_g": df_log["fibre_g"].sum(),
                    "alcohol_g": df_log["alcohol_g"].sum()
                }
        else:
            # No data for this date
            daily_totals = {
                "date": date_str,
                "calories": 0,
                "carbs_g": 0,
                "protein_g": 0,
                "fat_g": 0,
                "fibre_g": 0,
                "alcohol_g": 0
            }
        
        daily_data.append(daily_totals)
    
    # Create DataFrame for plotting
    df_trends = pd.DataFrame(daily_data)
    df_trends['date'] = pd.to_datetime(df_trends['date'])
    
    # Display charts
    if not df_trends.empty:
        # Calories trend
        st.subheader("📊 Daily Calories")
        fig_calories = px.line(df_trends, x='date', y='calories', 
                              title='Daily Calorie Intake',
                              labels={'calories': 'Calories (kcal)', 'date': 'Date'})
        fig_calories.update_traces(line_color='#ff6b6b', line_width=3)
        # Add 1800 calorie target line (dotted)
        fig_calories.add_shape(
            type="line",
            x0=df_trends['date'].min(), x1=df_trends['date'].max(),
            y0=1800, y1=1800,
            line=dict(color="#888", width=2, dash="dot"),
        )
        # Add annotation for the target line
        fig_calories.add_annotation(
            x=df_trends['date'].max(),
            y=1800,
            xref="x", yref="y",
            text="Target (1800 kcal)",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            font=dict(color="#888", size=12)
        )
        st.plotly_chart(fig_calories, use_container_width=True)
        
        # Macronutrients trend
        st.subheader("🥗 Macronutrients Breakdown")
        fig_macros = go.Figure()
        fig_macros.add_trace(go.Scatter(x=df_trends['date'], y=df_trends['carbs_g'], 
                                       mode='lines+markers', name='Carbs (g)', line_color='#4ecdc4'))
        fig_macros.add_trace(go.Scatter(x=df_trends['date'], y=df_trends['protein_g'], 
                                       mode='lines+markers', name='Protein (g)', line_color='#45b7d1'))
        fig_macros.add_trace(go.Scatter(x=df_trends['date'], y=df_trends['fat_g'], 
                                       mode='lines+markers', name='Fat (g)', line_color='#f9ca24'))
        fig_macros.add_trace(go.Scatter(x=df_trends['date'], y=df_trends['fibre_g'], 
                                       mode='lines+markers', name='Fibre (g)', line_color='#6c5ce7'))
        
        fig_macros.update_layout(title='Daily Macronutrients', 
                                xaxis_title='Date', 
                                yaxis_title='Grams')
        st.plotly_chart(fig_macros, use_container_width=True)
        
        # Summary statistics
        st.subheader("📋 Period Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_calories = df_trends['calories'].mean()
            st.metric("Avg Daily Calories", f"{avg_calories:.0f} kcal")
        
        with col2:
            avg_carbs = df_trends['carbs_g'].mean()
            st.metric("Avg Daily Carbs", f"{avg_carbs:.1f}g")
        
        with col3:
            avg_protein = df_trends['protein_g'].mean()
            st.metric("Avg Daily Protein", f"{avg_protein:.1f}g")
        
        with col4:
            avg_fat = df_trends['fat_g'].mean()
            st.metric("Avg Daily Fat", f"{avg_fat:.1f}g")
    
    else:
        st.info("No data available for the selected date range.")
        
else:
    st.error("Start date must be before or equal to end date.")
