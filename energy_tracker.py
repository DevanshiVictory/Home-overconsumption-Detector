import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Predefined energy-saving tips
ENERGY_TIPS = {
    "light": "💡 Switch to LED bulbs for better energy efficiency.",
    "fan": "🌬️ Use energy-efficient ceiling fans.",
    "air_conditioner": "❄️ Set AC temperature to 24°C for energy savings.",
    "fridge": "🧊 Keep refrigerator door closed tightly.",
    "tv": "📺 Turn off TV completely when not in use.",
    "computer": "🖥️ Enable power-saving mode on your computer.",
    "washer": "🧺 Run washer with full loads.",
}

st.set_page_config(page_title="Sustainable Energy Tracker", layout="wide")
st.title("⚡ Sustainable Home Energy Usage Tracker")

# File upload
uploaded_file = st.file_uploader("📁 Upload your energy consumption CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head())

    # Filter ON status
    active_df = df[df['status'] == 'on']

    if active_df.empty:
        st.warning("No devices are marked 'on' in the dataset.")
    else:
        # Group and calculate monthly kWh usage
        usage = active_df.groupby('device_type')['power_watt'].sum().reset_index()
        usage_counts = active_df['device_type'].value_counts().reset_index()
        usage_counts.columns = ['device_type', 'hours_on']
        merged = pd.merge(usage, usage_counts, on='device_type')
        merged['monthly_kWh'] = merged['power_watt'] / 1000  # Total kWh

        # Electricity cost input
        unit_cost = st.number_input("💰 Enter your electricity rate (₹ per kWh)", min_value=0.0, value=8.0)
        merged['estimated_cost'] = merged['monthly_kWh'] * unit_cost

        # Add tips
        merged['Energy Tip'] = merged['device_type'].apply(
            lambda x: ENERGY_TIPS.get(x.lower(), "✅ Use appliances wisely to save energy.")
        )

        # Show results
        st.subheader("📊 Monthly Energy Summary")
        st.dataframe(merged[['device_type', 'monthly_kWh', 'estimated_cost', 'Energy Tip']])

        # Plot
        st.subheader("📈 Monthly Usage by Appliance")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(merged['device_type'], merged['monthly_kWh'], color='skyblue')
        ax.set_xlabel("Appliance")
        ax.set_ylabel("Monthly Usage (kWh)")
        ax.set_title("Monthly Energy Usage per Appliance")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

        # Total summary
        total_usage = merged['monthly_kWh'].sum()
        total_cost = merged['estimated_cost'].sum()
        st.success(f"🌍 Total Monthly Usage: **{total_usage:.2f} kWh**")
        st.success(f"💸 Estimated Monthly Cost: **₹{total_cost:.2f}**")

else:
    st.info("Please upload a CSV file to begin.")
