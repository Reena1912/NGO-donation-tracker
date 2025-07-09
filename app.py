import streamlit as st
import pandas as pd
import plotly.express as px
import os

# File path
DATA_PATH = 'data/donations.csv'
os.makedirs('data', exist_ok=True)

# Load or create data
def load_data():
    # Handle missing or empty CSV
    if os.path.exists(DATA_PATH) and os.path.getsize(DATA_PATH) > 0:
        return pd.read_csv(DATA_PATH)
    else:
        df = pd.DataFrame(columns=['Name', 'Amount', 'Purpose', 'Location'])
        df.to_csv(DATA_PATH, index=False)
        return df

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

st.set_page_config(page_title="NGO Donation Tracker", layout="wide")

st.title("💝 NGO Donation Tracker & Impact Visualizer")

# Add donation form
with st.form("donation_form"):
    name = st.text_input("Donor Name")
    amount = st.number_input("Amount Donated (₹)", min_value=1)
    purpose = st.selectbox("Purpose", ["Education", "Health", "Food", "Shelter", "Other"])
    location = st.text_input("Donor Location")

    submitted = st.form_submit_button("Add Donation")
    if submitted:
        if name and location:
            new_data = pd.DataFrame([[name, amount, purpose, location]],
                                    columns=['Name', 'Amount', 'Purpose', 'Location'])
            data = load_data()
            data = pd.concat([data, new_data], ignore_index=True)
            save_data(data)
            st.success("✅ Donation added successfully!")
            st.rerun()

        else:
            st.error("Please fill all the fields.")

# Load and display donation records
data = load_data()

st.subheader("📄 Donation Records")
if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.info("No donations recorded yet.")

# Sidebar filters
st.sidebar.header("📍 Filter Donations")
filter_location = st.sidebar.multiselect("Filter by Location", options=data['Location'].unique())
filter_purpose = st.sidebar.multiselect("Filter by Purpose", options=data['Purpose'].unique())

filtered_data = data.copy()
if filter_location:
    filtered_data = filtered_data[filtered_data['Location'].isin(filter_location)]
if filter_purpose:
    filtered_data = filtered_data[filtered_data['Purpose'].isin(filter_purpose)]

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
else:
    st.warning("No data to display in charts. Try adjusting the filters.")
