import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Constants
DATA_PATH = 'data/donations.csv'
os.makedirs('data', exist_ok=True)

# Dummy login system
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title(" NGO Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "pass123":
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

if not st.session_state.logged_in:
    login()
    st.stop()

# Setup page
st.set_page_config(page_title="NGO Donation Tracker", layout="wide")
st.title(" NGO Donation Tracker & Impact Visualizer")

# Load and save functions
def load_data():
    if os.path.exists(DATA_PATH) and os.path.getsize(DATA_PATH) > 0:
        return pd.read_csv(DATA_PATH)
    else:
        df = pd.DataFrame(columns=['Name', 'Amount', 'Purpose', 'Location', 'Date'])
        df.to_csv(DATA_PATH, index=False)
        return df

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

# Donation Form
with st.form("donation_form"):
    name = st.text_input("Donor Name")
    amount = st.number_input("Amount Donated (₹)", min_value=1)
    purpose = st.selectbox("Purpose", ["Education", "Health", "Food", "Shelter", "Other"])
    location = st.text_input("Donor Location")

    submitted = st.form_submit_button("Add Donation")
    if submitted:
        if name and location:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = pd.DataFrame([[name, amount, purpose, location, date]],
                                    columns=['Name', 'Amount', 'Purpose', 'Location', 'Date'])
            data = load_data()
            data = pd.concat([data, new_data], ignore_index=True)
            save_data(data)
            st.success("✅ Donation added successfully!")
            st.rerun()
        else:
            st.error("Please fill all the fields.")

# Load data
data = load_data()

# Filters
st.sidebar.header("📍 Filter Donations")
filter_location = st.sidebar.multiselect("Filter by Location", options=data['Location'].unique())
filter_purpose = st.sidebar.multiselect("Filter by Purpose", options=data['Purpose'].unique())

filtered_data = data.copy()
if filter_location:
    filtered_data = filtered_data[filtered_data['Location'].isin(filter_location)]
if filter_purpose:
    filtered_data = filtered_data[filtered_data['Purpose'].isin(filter_purpose)]

# Search by name
search_name = st.text_input("🔍 Search Donor Name")
if search_name:
    filtered_data = filtered_data[filtered_data['Name'].str.contains(search_name, case=False)]

# Display table
st.subheader("📄 Donation Records")
if not filtered_data.empty:
    st.dataframe(filtered_data, use_container_width=True)
else:
    st.info("No donation records found.")

# Download CSV
if not filtered_data.empty:
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "donations_filtered.csv", "text/csv")

# Visualizations
if not filtered_data.empty:
    st.subheader("📊 Visual Insights")
    col1, col2 = st.columns(2)

    with col1:
        pie_chart = px.pie(filtered_data, names='Purpose', values='Amount', title='Donations by Purpose')
        st.plotly_chart(pie_chart, use_container_width=True)

    with col2:
        bar_chart = px.bar(filtered_data, x='Location', y='Amount', color='Purpose',
                           title='Donations by Location')
        st.plotly_chart(bar_chart, use_container_width=True)

    # Line chart - Donation trend
    if 'Date' in filtered_data.columns:
        try:
            filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])
            trend = filtered_data.groupby(filtered_data['Date'].dt.date)['Amount'].sum().reset_index()
            st.subheader("📆 Donation Trend Over Time")
            line_chart = px.line(trend, x='Date', y='Amount', title="Daily Donation Trend")
            st.plotly_chart(line_chart, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not parse dates: {e}")
else:
    st.warning("No data to display in charts. Try adjusting filters.")

# Geo Map (based on known cities)
location_coords = {
    'Delhi': (28.6139, 77.2090),
    'Mumbai': (19.0760, 72.8777),
    'Kolkata': (22.5726, 88.3639),
    'Chennai': (13.0827, 80.2707),
    'Bangalore': (12.9716, 77.5946)
}

filtered_data['lat'] = filtered_data['Location'].map(lambda loc: location_coords.get(loc, (None, None))[0])
filtered_data['lon'] = filtered_data['Location'].map(lambda loc: location_coords.get(loc, (None, None))[1])

map_df = filtered_data.dropna(subset=['lat', 'lon'])

if not map_df.empty:
    st.subheader("🗺️ Donations by Location")
    map_chart = px.scatter_geo(map_df,
                               lat='lat', lon='lon',
                               hover_name='Name', size='Amount',
                               color='Purpose',
                               projection="natural earth")
    st.plotly_chart(map_chart, use_container_width=True)
