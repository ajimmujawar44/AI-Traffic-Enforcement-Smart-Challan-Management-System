import streamlit as st

from src.database.models import get_all_challans, get_violation_history


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Challan History",
    page_icon="📋",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("📋 Challan History")

st.write(
    "View generated e-challans and violation history "
    "stored in the traffic enforcement database."
)

st.divider()


# ============================================================
# SEARCH
# ============================================================

search_plate = st.text_input(
    "🔎 Search by Vehicle Registration",
    placeholder="Example: TS09PA3330",
)

search_button = st.button(
    "Search History",
    type="primary",
)


# ============================================================
# DATA
# ============================================================

if search_button and search_plate.strip():

    challans = get_all_challans()

    plate = search_plate.strip().upper()

    filtered_challans = [
        challan
        for challan in challans
        if challan["vehicle_reg"].upper() == plate
    ]

    if filtered_challans:

        st.success(
            f"✅ Found {len(filtered_challans)} challan(s) "
            f"for {plate}"
        )

        st.subheader("📋 Challan Records")

        for challan in filtered_challans:

            with st.expander(
                f"🎫 {challan['challan_id']} — "
                f"{challan['violation_name']}"
            ):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Vehicle",
                        challan["vehicle_reg"],
                    )

                with col2:
                    st.metric(
                        "Violation",
                        challan["violation_name"],
                    )

                with col3:
                    st.metric(
                        "Fine",
                        f"₹{challan['fine']}",
                    )

                st.write(
                    f"**Detected At:** "
                    f"{challan['detected_at']}"
                )

                st.write(
                    f"**Status:** "
                    f"{challan['status']}"
                )

    else:

        st.warning(
            f"⚠️ No challans found for vehicle "
            f"'{plate}'."
        )


elif search_button:

    st.warning(
        "Please enter a vehicle registration number."
    )


# ============================================================
# ALL CHALLANS
# ============================================================

st.divider()

st.subheader("📊 All Challans")

all_challans = get_all_challans()

if all_challans:

    st.write(
        f"Total Challans: **{len(all_challans)}**"
    )

    st.dataframe(
        all_challans,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "ℹ️ No challans have been generated yet."
    )


# ============================================================
# VEHICLE VIOLATION HISTORY
# ============================================================

st.divider()

st.subheader("🚨 Vehicle Violation History")

history_plate = st.text_input(
    "Enter vehicle number to view violation history",
    placeholder="Example: TS10ED8176",
    key="history_plate",
)

history_button = st.button(
    "View Violation History"
)


if history_button:

    if not history_plate.strip():

        st.warning(
            "Please enter a vehicle registration number."
        )

        st.stop()

    history = get_violation_history(
        history_plate.strip()
    )

    if history:

        st.success(
            f"Found {len(history)} violation record(s)."
        )

        st.dataframe(
            history,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            f"No violation history found for "
            f"'{history_plate.strip().upper()}'."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Traffic Enforcement & Smart Challan System • "
    "Developed by Ajim Mujawar"
)