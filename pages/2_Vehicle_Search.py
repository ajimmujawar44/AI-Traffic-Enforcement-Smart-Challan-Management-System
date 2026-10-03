import streamlit as st

from src.database.models import find_vehicle


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Vehicle Search",
    page_icon="🚗",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🚗 Vehicle Search")

st.write(
    "Search the registered vehicle database using "
    "a vehicle registration number."
)

st.divider()


# ============================================================
# SEARCH
# ============================================================

number_plate = st.text_input(
    "🔎 Vehicle Registration Number",
    placeholder="Example: TS10ED8176",
)


search_button = st.button(
    "Search Vehicle",
    type="primary",
)


# ============================================================
# SEARCH RESULT
# ============================================================

if search_button:

    if not number_plate.strip():

        st.warning(
            "Please enter a vehicle registration number."
        )

        st.stop()

    vehicle = find_vehicle(
        number_plate.strip()
    )

    if vehicle:

        st.success("✅ Vehicle found in database.")

        st.subheader("🚗 Vehicle Details")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Owner Name",
                vehicle["owner_name"],
            )

            st.metric(
                "Vehicle Registration",
                vehicle["vehicle_reg"],
            )

            st.metric(
                "Vehicle Type",
                vehicle["vehicle_type"],
            )

        with col2:

            st.metric(
                "Vehicle ID",
                vehicle["vehicle_id"],
            )

            st.metric(
                "Mobile",
                vehicle["mobile"],
            )

        st.divider()

        st.subheader("📋 Complete Vehicle Record")

        st.json(vehicle)

    else:

        st.warning(
            f"⚠️ Vehicle '{number_plate.upper()}' "
            "was not found in the registered database."
        )


# ============================================================
# DEMO VEHICLES
# ============================================================

st.divider()

st.subheader("🧪 Demo Vehicles")

st.caption(
    "These vehicles are included for demonstration "
    "and testing purposes."
)

demo_vehicles = [
    "TS09PA3330",
    "MH12AB1234",
    "KA01AA5678",
    "TS10ED8176",
]

for plate in demo_vehicles:

    st.code(plate)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Traffic Enforcement & Smart Challan System • "
    "Developed by Ajim Mujawar"
)