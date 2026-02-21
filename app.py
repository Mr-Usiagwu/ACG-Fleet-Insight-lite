import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from engine import generate_fleet_data, apply_risk_logic

# 1. Page Configuration (MUST be the first Streamlit command)
st.set_page_config(
    page_title="ACG Fleet Insight – Lite", 
    layout="wide", 
    page_icon="✈️"
)

# 2. Branded Sidebar Logo
try:
    logo = Image.open("acg_logo.jpeg")
    # Using use_column_width for compatibility with your Streamlit version
    st.sidebar.image(logo, use_column_width=True)
except Exception as e:
    st.sidebar.warning("Logo file 'acg_logo.jpg' not found on GitHub.")

# 3. Data Initialization (Persistence via Session State)
if 'fleet_df' not in st.session_state:
    raw_data = generate_fleet_data()
    st.session_state.fleet_df = apply_risk_logic(raw_data)

# 4. Sidebar - Global Controls
st.sidebar.title("✈️ ACG Fleet Insight")
st.sidebar.markdown("---")

role = st.sidebar.selectbox("Select User Role", ["Executive", "Operations", "Finance"])

# Settings
st.sidebar.subheader("Settings")
cost_per_point = st.sidebar.slider("Delay Cost Multiplier ($)", 100, 1000, 500)

# Apply the slider impact to a copy for display
df = st.session_state.fleet_df.copy()
df['Financial_Exposure'] = (df['Risk_Score'] * cost_per_point).round(0)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Fleet Data"):
    st.session_state.clear()
    st.rerun()

# 5. Role-Based Logic
if role == "Operations":
    st.header("🔧 Technical Operations Dashboard")
    
    # Priority Alerts
    st.subheader("⚠️ Maintenance Priority Alerts")
    critical_planes = df[df['Risk_Score'] > 60]
    if not critical_planes.empty:
        for _, row in critical_planes.iterrows():
            st.error(f"**ALERT:** {row['Tail_Number']} - Risk Score: {row['Risk_Score']} | Check Required.")
    else:
        st.success("All systems green. No critical alerts.")

    # Maintenance Action Interaction
    st.markdown("---")
    st.subheader("🛠️ Maintenance Action")
    with st.expander("Log Maintenance Activity"):
        selected_tail = st.selectbox("Select Tail Number to Clear Faults", df['Tail_Number'])
        if st.button("Perform Maintenance"):
            st.session_state.fleet_df.loc[st.session_state.fleet_df['Tail_Number'] == selected_tail, 'Technical_Faults'] = 0
            st.session_state.fleet_df.loc[st.session_state.fleet_df['Tail_Number'] == selected_tail, 'Days_Since_Check'] = 0
            st.session_state.fleet_df = apply_risk_logic(st.session_state.fleet_df)
            st.balloons()
            st.success(f"Maintenance logged for {selected_tail}. Risk reset!")
            st.rerun()

    st.subheader("Fleet Technical Status")
    st.dataframe(df[['Tail_Number', 'Model', 'Flight_Hours', 'Technical_Faults', 'Risk_Score']], use_container_width=True)

elif role == "Finance":
    st.header("💰 Financial Impact & Exposure")
    
    total_exposure = df['Financial_Exposure'].sum()
    st.metric("Total Fleet Risk Exposure", f"${total_exposure:,.0f}", help="Calculated based on Risk Score * Multiplier")
    
    st.subheader("💵 Risk-to-Cost Exposure Analysis")
    fig_finance = px.scatter(df, 
                             x="Risk_Score", 
                             y="Financial_Exposure",
                             size="Flight_Hours", 
                             color="Model",
                             hover_name="Tail_Number",
                             title="Financial Exposure vs. Technical Risk Score")
    st.plotly_chart(fig_finance, use_container_width=True)

else: # Executive View
    st.header("📊 Executive Fleet Health Overview")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Fleet Risk", f"{df['Risk_Score'].mean():.1f}")
    col2.metric("Highest Risk Tail", df.loc[df['Risk_Score'].idxmax(), 'Tail_Number'])
    col3.metric("Projected Loss (Fleet)", f"${df['Financial_Exposure'].sum():,.0f}")

    st.markdown("---")
    st.subheader("🌐 Global Fleet Health Heatmap")
    fig_heat = px.treemap(df, 
                          path=['Model', 'Tail_Number'], 
                          values='Risk_Score',
                          color='Risk_Score', 
                          color_continuous_scale='RdYlGn_r',
                          title="Fleet Risk Distribution")

    st.plotly_chart(fig_heat, use_container_width=True)

