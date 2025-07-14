import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Energy tips dictionary
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

# Session state for manual input
if "manual_appliances" not in st.session_state:
    st.session_state.manual_appliances = []

# -------------------
# 🔧 Manual Entry Form
# -------------------
with st.expander("➕ Manually Add Appliance (Optional)"):
    name = st.text_input("Appliance Name")
    power = st.number_input("Power Rating (Watts)", min_value=1)
    hours = st.number_input("Total Hours Used This Month", min_value=0.0)
    if st.button("Add Appliance"):
        if name and power > 0 and hours > 0:
            st.session_state.manual_appliances.append({
                "device_type": name,
                "power_rating": power,
                "hours_on": hours
            })
            st.success(f"✅ Added: {name}")
        else:
            st.error("Please enter all values correctly.")

# -------------------
# 📁 CSV Upload
# -------------------
uploaded_file = st.file_uploader("📁 Upload CSV File", type="csv")
if uploaded_file:
    raw_df = pd.read_csv(uploaded_file)
    st.subheader("📄 Raw Data Preview")
    st.dataframe(raw_df.head())

    # Use only rows with 'on' status
    csv_df = raw_df[raw_df['status'].str.lower() == 'on'].copy()
    csv_df["power_rating"] = csv_df["power_watt"]
    csv_df["hours_on"] = 1  # Assume each row = 1 hour
    csv_df = csv_df[["device_type", "power_rating", "hours_on"]]
else:
    csv_df = pd.DataFrame(columns=["device_type", "power_rating", "hours_on"])

# -------------------
# 📊 Combine Both Sources
# -------------------
manual_df = pd.DataFrame(st.session_state.manual_appliances)
combined_df = pd.concat([csv_df, manual_df], ignore_index=True)

if combined_df.empty:
    st.info("📥 Upload a CSV or enter appliance details manually.")
else:
    combined_df["total_energy_wh"] = combined_df["power_rating"] * combined_df["hours_on"]
    grouped = combined_df.groupby("device_type")["total_energy_wh"].sum().reset_index()
    grouped["monthly_kWh"] = grouped["total_energy_wh"] / 1000

    # ⚡ Electricity rate
    unit_cost = st.number_input("💰 Electricity rate (₹/kWh)", value=8.0)
    grouped["estimated_cost"] = grouped["monthly_kWh"] * unit_cost

    # Add energy-saving tips
    grouped["Energy Tip"] = grouped["device_type"].apply(
        lambda x: ENERGY_TIPS.get(x.lower(), "✅ Use appliances wisely to save energy.")
    )

    # ---------------------
    # 📋 Summary Table
    # ---------------------
    st.subheader("📊 Monthly Energy Summary")
    st.dataframe(grouped[["device_type", "monthly_kWh", "estimated_cost", "Energy Tip"]])

    # ---------------------
    # ⬇️ CSV Export
    # ---------------------
    st.download_button(
        label="⬇️ Download Report as CSV",
        data=grouped.to_csv(index=False),
        file_name="energy_report.csv",
        mime="text/csv"
    )

    # ---------------------
    # 📈 Bar Chart
    # ---------------------
    st.subheader("📈 Monthly Usage by Appliance (kWh)")
    fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
    ax_bar.bar(grouped['device_type'], grouped['monthly_kWh'], color='skyblue')
    ax_bar.set_xlabel("Appliance")
    ax_bar.set_ylabel("Monthly Usage (kWh)")
    ax_bar.set_title("Monthly Energy Usage per Appliance")
    ax_bar.tick_params(axis='x', rotation=45)
    st.pyplot(fig_bar)

    # ---------------------
    # 🥧 Pie Chart
    # ---------------------
    st.subheader("🥧 Energy Usage Distribution")
    fig_pie, ax_pie = plt.subplots()
    ax_pie.pie(
        grouped['monthly_kWh'],
        labels=grouped['device_type'],
        autopct='%1.1f%%',
        startangle=90,
        colors=plt.cm.Paired.colors
    )
    ax_pie.axis('equal')
    st.pyplot(fig_pie)

    # ---------------------
    # ✅ Total Usage & Goal
    # ---------------------
    total_kwh = grouped["monthly_kWh"].sum()
    total_cost = grouped["estimated_cost"].sum()
    st.success(f"🌍 Total Monthly Usage: **{total_kwh:.2f} kWh**")
    st.success(f"💸 Estimated Monthly Cost: **₹{total_cost:.2f}**")

    # 🎯 Goal Tracker
    st.markdown("---")
    st.subheader("🎯 Set a Monthly Usage Goal")
    goal_kwh = st.number_input("Your Goal (kWh):", min_value=0.0, value=100.0)
    if total_kwh > goal_kwh:
        st.error(f"⚠️ Goal exceeded by **{total_kwh - goal_kwh:.2f} kWh**.")
    else:
        st.success(f"✅ Within goal by **{goal_kwh - total_kwh:.2f} kWh**.")

    # ---------------------
    # 💡 Tips
    # ---------------------
    st.markdown("---")
    st.subheader("🧠 General Energy Saving Tips")
    st.markdown("""
    - 🌞 Use natural daylight when possible.
    - 🔌 Unplug devices when not in use.
    - 🚿 Use cold water for washing.
    - ⏲️ Limit heavy appliance usage during peak hours.
    - 🧼 Maintain fridge and AC regularly.
    """)
