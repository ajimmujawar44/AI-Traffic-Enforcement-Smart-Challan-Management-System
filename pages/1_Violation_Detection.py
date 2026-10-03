import os
import streamlit as st

from src.ai.violation_detector import analyze_traffic_image
from src.utils.image_utils import validate_image


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Violation Detection",
    page_icon="🚨",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🚨 AI Violation Detection")

st.write(
    "Upload traffic evidence and let the AI system "
    "detect the traffic violation and number plate."
)

st.divider()


# ============================================================
# UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📤 Upload Traffic Evidence",
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload a clear traffic image.",
)


# ============================================================
# PROCESS IMAGE
# ============================================================

if uploaded_file is not None:

    temp_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "temp",
    )

    os.makedirs(temp_dir, exist_ok=True)

    image_path = os.path.join(
        temp_dir,
        uploaded_file.name,
    )

    with open(image_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    try:

        validate_image(image_path)

    except Exception as error:

        st.error(f"Invalid image: {error}")
        st.stop()

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    st.subheader("📸 Evidence Preview")

    st.image(
        uploaded_file,
        caption="Traffic evidence",
        width="stretch",
    )

    st.divider()

    # --------------------------------------------------------
    # ANALYZE
    # --------------------------------------------------------

    if st.button(
        "🔍 Detect Violation",
        type="primary",
        width="stretch",
    ):

        with st.spinner(
            "🤖 AI is analyzing the image..."
        ):

            try:

                result = analyze_traffic_image(
                    image_path
                )

            except Exception as error:

                st.error(
                    f"AI detection failed: {error}"
                )

                st.stop()

        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        violation = result.get(
            "violation",
            "Unknown",
        )

        number_plate = result.get(
            "number_plate",
            "Not Detected",
        )

        valid_violation = result.get(
            "valid_violation",
            False,
        )

        st.success(
            "✅ AI analysis completed."
        )

        st.subheader("🚨 Detection Results")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Violation",
                violation,
            )

        with col2:

            st.metric(
                "Number Plate",
                number_plate,
            )

        with col3:

            status = (
                "Valid"
                if valid_violation
                else "Unsupported"
            )

            st.metric(
                "Status",
                status,
            )

        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        st.divider()

        if valid_violation:

            st.success(
                f"🚨 Detected violation: **{violation}**"
            )

        else:

            st.warning(
                "The detected violation is not currently "
                "supported by the challan system."
            )

else:

    st.info(
        "📤 Upload an image to start AI violation detection."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Traffic Enforcement & Smart Challan System • "
    "Developed by Ajim Mujawar"
)