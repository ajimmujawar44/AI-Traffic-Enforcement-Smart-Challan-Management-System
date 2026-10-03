import os
import streamlit as st

from src.ai.violation_detector import analyze_traffic_image
from src.database.models import get_dashboard_statistics
from src.challan.service import create_e_challan
from src.utils.image_utils import validate_image


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Traffic Enforcement",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        opacity: 0.7;
        margin-bottom: 25px;
    }

    .status {
        display: inline-block;
        padding: 7px 15px;
        border-radius: 20px;
        background: rgba(0, 190, 110, 0.10);
        border: 1px solid rgba(0, 190, 110, 0.35);
        font-weight: 700;
        margin-bottom: 25px;
    }

    .card {
        border: 1px solid rgba(120,130,150,0.25);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .card-title {
        font-size: 13px;
        opacity: 0.65;
        margin-bottom: 6px;
    }

    .card-value {
        font-size: 24px;
        font-weight: 800;
    }

    .success-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(0,190,110,0.35);
        background: rgba(0,190,110,0.08);
        margin: 15px 0;
    }

    .footer {
        text-align: center;
        opacity: 0.5;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid rgba(120,130,150,0.2);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🚦 Traffic Enforcement")

    st.markdown("---")

    st.markdown("### Navigation")

    st.write("📸 Violation Detection")
    st.write("🚗 Vehicle Verification")
    st.write("📄 E-Challan Generation")
    st.write("📊 Enforcement Analytics")

    st.markdown("---")

    st.markdown("### System Status")

    st.success("● System Online")

    st.caption("AI Detection: Ready")
    st.caption("Vehicle Database: Connected")
    st.caption("Challan Engine: Ready")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🚦 AI Traffic Enforcement</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered traffic violation detection, vehicle verification "
    "and automated e-challan generation"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="status">● SYSTEM ONLINE</div>',
    unsafe_allow_html=True,
)


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
        "🚨 Violations",
        stats["total_violations"],
    )

with col3:
    st.metric(
        "🎫 Challans",
        stats["total_challans"],
    )

with col4:
    st.metric(
        "💰 Total Fines",
        f"₹{stats['total_fines']}",
    )


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown("## 📤 Upload Traffic Evidence")

st.write(
    "Upload an image containing a possible traffic violation. "
    "The AI system will analyze the image and detect the violation "
    "and number plate."
)

uploaded_file = st.file_uploader(
    "Choose traffic evidence",
    type=["jpg", "jpeg", "png", "webp"],
    help="Supported formats: JPG, JPEG, PNG and WEBP.",
)


# ============================================================
# IMAGE PROCESSING
# ============================================================

if uploaded_file is not None:

    # --------------------------------------------------------
    # SAVE UPLOADED IMAGE
    # --------------------------------------------------------

    temp_dir = os.path.join(
        os.path.dirname(__file__),
        "temp",
    )

    os.makedirs(
        temp_dir,
        exist_ok=True,
    )

    image_path = os.path.join(
        temp_dir,
        uploaded_file.name,
    )

    with open(image_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    # --------------------------------------------------------
    # VALIDATE IMAGE
    # --------------------------------------------------------

    try:

        validate_image(image_path)

    except Exception as error:

        st.error(
            f"❌ Invalid image: {error}"
        )

        st.stop()

    # --------------------------------------------------------
    # IMAGE PREVIEW
    # --------------------------------------------------------

    st.markdown("## 📸 Evidence Preview")

    st.image(
        uploaded_file,
        caption="Uploaded traffic evidence",
        width="stretch",
    )

    st.markdown("---")

    # --------------------------------------------------------
    # ANALYZE BUTTON
    # --------------------------------------------------------

    analyze_button = st.button(
        "🔍 Analyze Traffic Violation",
        type="primary",
        width="stretch",
    )

    if analyze_button:

        # ====================================================
        # AI ANALYSIS
        # ====================================================

        with st.spinner(
            "🤖 AI is analyzing the traffic evidence..."
        ):

            try:

                result = analyze_traffic_image(
                    image_path
                )

            except Exception as error:

                st.error(
                    f"❌ AI analysis failed: {error}"
                )

                st.stop()

        # ====================================================
        # EXTRACT AI RESULT
        # ====================================================

        violation = result.get(
            "violation",
            "Unknown",
        )

        number_plate = result.get(
            "number_plate",
            "",
        )

        valid_violation = result.get(
            "valid_violation",
            False,
        )

        # ====================================================
        # AI ANALYSIS SUCCESS
        # ====================================================

        st.success(
            "✓ AI analysis completed successfully."
        )

        # ====================================================
        # DETECTION RESULT
        # ====================================================

        st.markdown("## 🚨 Detection Result")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                label="Detected Violation",
                value=str(violation),
            )

        with col2:

            display_plate = (
                number_plate
                if number_plate
                else "Not Detected"
            )

            st.metric(
                label="Number Plate",
                value=str(display_plate),
            )

        with col3:

            status = (
                "Valid Violation"
                if valid_violation
                else "Not Supported"
            )

            st.metric(
                label="Detection Status",
                value=status,
            )

        # ====================================================
        # INVALID VIOLATION
        # ====================================================

        if not valid_violation:

            st.warning(
                "⚠️ The detected violation is not currently "
                "supported by the challan system."
            )

            st.stop()

        # ====================================================
        # NUMBER PLATE CHECK
        # ====================================================

        if (
            not number_plate
            or number_plate.strip().upper()
            in {
                "NOT DETECTED",
                "UNKNOWN",
                "NONE",
            }
        ):

            st.warning(
                "⚠️ Number plate could not be detected. "
                "Please upload a clearer image where the "
                "vehicle registration number is visible."
            )

            st.stop()

        # ====================================================
        # CREATE E-CHALLAN
        # ====================================================

        with st.spinner(
            "🎫 Generating e-challan..."
        ):

            try:

                challan_result = create_e_challan(
                    vehicle_reg=number_plate,
                    violation=violation,
                )

            except Exception as error:

                st.error(
                    f"❌ Challan generation failed: {error}"
                )

                st.stop()

        # ====================================================
        # CHALLAN SUCCESS
        # ====================================================

        st.success(
            "✅ E-Challan generated successfully."
        )

        # ====================================================
        # CHALLAN DETAILS
        # ====================================================

        st.markdown("## 🎫 E-Challan Details")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                label="Challan ID",
                value=str(
                    challan_result["challan_id"]
                ),
            )

        with col2:

            st.metric(
                label="Vehicle",
                value=str(
                    challan_result["vehicle"][
                        "vehicle_reg"
                    ]
                ),
            )

        with col3:

            st.metric(
                label="Fine Amount",
                value=f"₹{challan_result['fine']}",
            )

        # ====================================================
        # OWNER / VEHICLE DETAILS
        # ====================================================

        vehicle = challan_result["vehicle"]

        st.markdown(
            "## 👤 Registered Vehicle Owner"
        )

        owner_col1, owner_col2 = st.columns(2)

        with owner_col1:

            st.subheader(
                "👤 Owner Information"
            )

            st.write(
                f"**Owner Name:** "
                f"{vehicle['owner_name']}"
            )

            st.write(
                f"**Vehicle Registration:** "
                f"{vehicle['vehicle_reg']}"
            )

            st.write(
                f"**Vehicle ID:** "
                f"{vehicle['vehicle_id']}"
            )

        with owner_col2:

            st.subheader(
                "🚗 Vehicle Information"
            )

            st.write(
                f"**Vehicle Type:** "
                f"{vehicle['vehicle_type']}"
            )

            st.write(
                f"**Contact:** "
                f"{vehicle['mobile']}"
            )

            st.write(
                f"**Violation:** "
                f"{challan_result['violation']}"
            )

        st.divider()

        # ====================================================
        # PDF DOWNLOAD
        # ====================================================

        st.markdown("## 📄 E-Challan PDF")

        pdf_path = challan_result["pdf_path"]

        if os.path.exists(pdf_path):

            st.success(
                "✅ PDF e-Challan has been generated automatically."
            )

            with open(
                pdf_path,
                "rb",
            ) as pdf_file:

                pdf_data = pdf_file.read()

            st.download_button(
                label="⬇️ Download E-Challan PDF",
                data=pdf_data,
                file_name=os.path.basename(
                    pdf_path
                ),
                mime="application/pdf",
                type="primary",
                width="stretch",
            )

        else:

            st.warning(
                "⚠️ E-Challan PDF was not generated."
            )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.info(
        "📤 Upload a traffic violation image "
        "to start AI analysis."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        🚦 AI Traffic Enforcement & Smart Challan System

        <br>

        Built with Python • Streamlit • Groq AI • SQLite • ReportLab

        <br><br>

        Developed by <b>Ajim Mujawar</b>

    </div>
    """,
    unsafe_allow_html=True,
)