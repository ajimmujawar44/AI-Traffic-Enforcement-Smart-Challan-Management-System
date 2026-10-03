import streamlit as st
import pandas as pd

from src.database.models import (
    get_dashboard_statistics,
    get_all_challans,
    get_all_violations,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 Traffic Enforcement Analytics")

st.write(
    "Monitor vehicles, violations, challans and fine "
    "collection through the traffic enforcement database."
)

st.divider()


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

stats = get_dashboard_statistics()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🚗 Registered Vehicles",
        stats["total_vehicles"],
    )

with col2:
    st.metric(
        "🚨 Total Violations",
        stats["total_violations"],
    )

with col3:
    st.metric(
        "🎫 Total Challans",
        stats["total_challans"],
    )

with col4:
    st.metric(
        "💰 Total Fines",
        f"₹{stats['total_fines']}",
    )


# ============================================================
# VIOLATION TYPES
# ============================================================

st.divider()

st.subheader("🚨 Violation Types")

violations = get_all_violations()

if violations:

    violation_df = pd.DataFrame(violations)

    st.dataframe(
        violation_df,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No violation types are configured."
    )


# ============================================================
# CHALLAN ANALYTICS
# ============================================================

st.divider()

st.subheader("🎫 Challan Analytics")

challans = get_all_challans()

if challans:

    challan_df = pd.DataFrame(challans)

    # --------------------------------------------------------
    # Violation count
    # --------------------------------------------------------

    violation_counts = (
        challan_df["violation_name"]
        .value_counts()
        .reset_index()
    )

    violation_counts.columns = [
        "Violation",
        "Count",
    ]

    st.write("### 📈 Challans by Violation")

    st.bar_chart(
        violation_counts.set_index("Violation")
    )

    # --------------------------------------------------------
    # Fine distribution
    # --------------------------------------------------------

    fine_summary = (
        challan_df.groupby("violation_name")["fine"]
        .sum()
        .reset_index()
    )

    fine_summary.columns = [
        "Violation",
        "Total Fine",
    ]

    st.write("### 💰 Fine Distribution")

    st.bar_chart(
        fine_summary.set_index("Violation")
    )

    # --------------------------------------------------------
    # Challan table
    # --------------------------------------------------------

    st.write("### 📋 Challan Data")

    st.dataframe(
        challan_df,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "ℹ️ No challans available for analytics yet."
    )


# ============================================================
# SUMMARY
# ============================================================

st.divider()

st.subheader("📌 Dashboard Summary")

if stats["total_challans"] > 0:

    average_fine = (
        stats["total_fines"]
        / stats["total_challans"]
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Average Fine per Challan",
            f"₹{average_fine:.2f}",
        )

    with col2:
        st.metric(
            "Total Fine Amount",
            f"₹{stats['total_fines']}",
        )

else:

    st.info(
        "Generate some challans to populate analytics."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Traffic Enforcement & Smart Challan System • "
    "Developed by Ajim Mujawar"
)