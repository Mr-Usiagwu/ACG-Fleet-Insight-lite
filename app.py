import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. SETUP & BRANDING
st.set_page_config(page_title="ACG ERP | Fleet Manager", layout="wide", page_icon="✈️")

# Simulated Database (In a real ERP, this would be a Google Sheet)
if 'erp_data' not in st.session_state:
    st.session_state.erp_data = pd.DataFrame(columns=[
        'Date', 'Tail_Number', 'Crew', 'Origin', 'Destination', 
        'Passengers', 'Revenue', 'Expenses', 'Profit', 'Type'
    ])

# 2. AUTOMATION LOGIC (The "Math" Engine)
def calculate_flight_finances(pax, dist_category):
    # Assume $250 avg ticket price
    rev = pax * 250 
    # Categorize expenses based on flight length
    costs = {"Short Haul": 5000, "Medium Haul": 12000, "Long Haul": 25000}
    exp = costs.get(dist_category, 10000) + (pax * 15) # Add $15 per head for catering/taxes
    return rev, exp

# 3. SIDEBAR NAVIGATION
st.sidebar.title("✈️ ACG ERP System")
menu = st.sidebar.radio("Command Menu", ["Dashboard", "Log New Flight", "Fleet Timeline", "Maintenance Log"])

# --- PAGE 1: SMART DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Fleet Performance Intelligence")
    
    if st.session_state.erp_data.empty:
        st.info("Your logbook is empty. Go to 'Log New Flight' to start your ERP data.")
    else:
        df = st.session_state.erp_data
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Revenue", f"${df['Revenue'].sum():,.2f}")
        c2.metric("Total Expenses", f"${df['Expenses'].sum():,.2f}")
        c3.metric("Net Profit", f"${df['Profit'].sum():,.2f}", delta=f"{df['Profit'].mean():,.2f} avg/flight")

        st.subheader("Profitability by Aircraft")
        fig = px.bar(df, x="Tail_Number", y="Profit", color="Destination", barmode="group",
                     title="Earnings per Tail Number")
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 2: LOG NEW FLIGHT (THE INPUT) ---
elif menu == "Log New Flight":
    st.title("📝 Operations Input")
    st.subheader("Enter flight details - The ERP will calculate financials automatically.")
    
    with st.form("flight_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            date = st.date_input("Flight Date", datetime.now())
            tail = st.selectbox("Aircraft Tail", ["ACG-101", "ACG-102", "ACG-103", "ACG-104"])
            crew = st.text_input("Crew Names", placeholder="Capt. Smith / FO Jones")
        with c2:
            dist = st.selectbox("Route Type", ["Short Haul", "Medium Haul", "Long Haul"])
            pax = st.number_input("Passenger Count", min_value=1, max_value=300, value=150)
            route = st.text_input("Route (e.g. LHR - JFK)")

        if st.form_submit_button("Finalize & Post to Ledger"):
            rev, exp = calculate_flight_finances(pax, dist)
            new_entry = {
                'Date': date, 'Tail_Number': tail, 'Crew': crew, 
                'Origin': route.split('-')[0] if '-' in route else "Unknown",
                'Destination': route.split('-')[1] if '-' in route else route,
                'Passengers': pax, 'Revenue': rev, 'Expenses': exp, 
                'Profit': rev - exp, 'Type': 'Flight'
            }
            st.session_state.erp_data = pd.concat([st.session_state.erp_data, pd.DataFrame([new_entry])], ignore_index=True)
            st.success(f"Flight Logged! Profit Generated: ${rev-exp:,.2f}")
            st.balloons()

# --- PAGE 3: FLEET TIMELINE ---
elif menu == "Fleet Timeline":
    st.title("📅 30-Day Operations Timeline")
    
    if st.session_state.erp_data.empty:
        st.warning("No flight history found.")
    else:
        df = st.session_state.erp_data
        # Gantt-style chart for the month
        fig = px.timeline(df, x_start="Date", x_end="Date", y="Tail_Number", color="Profit",
                          hover_data=["Crew", "Passengers", "Destination"],
                          title="Monthly Fleet Schedule & Earnings")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Full Ledger (Consise Report)")
        st.dataframe(df[['Date', 'Tail_Number', 'Crew', 'Destination', 'Profit']], use_container_width=True)

# --- PAGE 4: MAINTENANCE LOG ---
elif menu == "Maintenance Log":
    st.title("🔧 Maintenance Schedule")
    st.write("Next Mandatory Checks based on 30-day cycle:")
    
    # Simple automated logic for next check
    for aircraft in ["ACG-101", "ACG-102", "ACG-103", "ACG-104"]:
        next_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        st.write(f"✈️ **{aircraft}**: Next A-Check scheduled for **{next_date}**")
