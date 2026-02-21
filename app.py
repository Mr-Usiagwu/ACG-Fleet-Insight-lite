import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from engine import generate_fleet_data, apply_risk_logic

# 1. Page Config
st.set_page_config(page_title="ACG Fleet Manager Pro", layout="wide", page_icon="✈️")

# 2. Logo Handling
try:
    logo = Image.open("acg_logo.jpg")
    st.sidebar.image(logo, use_column_width=True)
except:
    st.sidebar.info("Upload 'acg_logo.jpg' to GitHub to see your branding.")

# 3. Enhanced Data Initialization
# We add new columns for the details you want to track
if 'fleet_df' not in st.session_state:
    df = apply_risk_logic(generate_fleet_data())
    # Initialize new columns with default values
    df['Last_Crew'] = "Unassigned"
    df['Fuel_Used_KG'] = 0
    df['Expenses_$'] = 0
    df['Revenue_$'] = 0
    df['Next_Departure'] = "TBD"
    df['Profit_$'] = 0
    st.session_state.fleet_df = df

df = st.session_state.fleet_df

# 4. Sidebar Navigation
st.sidebar.title("🎮 Command Center")
page = st.sidebar.radio("Go to:", ["Global Fleet Dashboard", "Log Flight & Expenses", "Aircraft Deep Dive"])

# --- PAGE 1: GLOBAL DASHBOARD ---
if page == "Global Fleet Dashboard":
    st.header("📊 Global Fleet Health & Profitability")
    
    # Top Level Metrics
    c1, c2, c3, c4 = st.columns(4)
    total_profit = df['Profit_$'].sum()
    c1.metric("Total Fleet Profit", f"${total_profit:,.2f}")
    c2.metric("Avg Risk Score", f"{df['Risk_Score'].mean():.1f}")
    c3.metric("Total Fuel Burn (KG)", f"{df['Fuel_Used_KG'].sum():,.0f}")
    c4.metric("Active Tails", len(df))

    st.subheader("Financial Performance by Aircraft")
    fig = px.bar(df, x="Tail_Number", y="Profit_$", color="Risk_Score", 
                 title="Profitability per Tail (Color = Risk Level)",
                 color_continuous_scale='RdYlGn_r')
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 2: DATA ENTRY ---
elif page == "Log Flight & Expenses":
    st.header("📝 Daily Operations Log")
    st.info("Input the details of the most recent flight here to update the fleet records.")
    
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            target_tail = st.selectbox("Select Aircraft", df['Tail_Number'])
            crew = st.text_input("Crew Members", placeholder="e.g. Capt. Smith, FO Jones")
            fuel = st.number_input("Fuel Consumed (KG)", min_value=0)
        with col2:
            rev = st.number_input("Flight Revenue ($)", min_value=0)
            exp = st.number_input("Other Expenses ($)", min_value=0)
            dest = st.text_input("Next Destination", placeholder="e.g. LHR, JFK, DXB")
        
        if st.form_submit_button("Update Aircraft Records"):
            # Update the specific row in Session State
            idx = df.index[df['Tail_Number'] == target_tail][0]
            st.session_
