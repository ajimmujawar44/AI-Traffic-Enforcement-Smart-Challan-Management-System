from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "generated_challans"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# PDF GENERATOR
# ============================================================

def generate_challan_pdf(
    challan_id,
    vehicle,
    violation,
    fine,
    ai_confidence=None,
    output_dir=OUTPUT_DIR,
):
    """
    Generate a professional PDF e-Challan.

    Parameters
    ----------
    challan_id : str
        Unique challan identifier.

    vehicle : dict
        Vehicle/owner information.

    violation : str
        Detected traffic violation.

    fine : int | float
        Fine amount.

    ai_confidence : float | None
        Optional AI confidence score.

    output_dir : Path
        Directory where PDF will be saved.

    Returns
    -------
    Path
        Path of generated PDF.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now()
    filename = f"{challan_id}.pdf"
    pdf_path = output_dir / filename

    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ChallanTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
    )

    # --------------------------------------------------------
    # VEHICLE DATA
    # --------------------------------------------------------

    owner_name = vehicle.get("owner_name", "N/A")
    number_plate = vehicle.get("number_plate", "N/A")
    vehicle_type = vehicle.get("vehicle_type", "N/A")
    vehicle_id = vehicle.get("vehicle_id", "N/A")
    phone = vehicle.get("phone", "N/A")

    # --------------------------------------------------------
    # STORY
    # --------------------------------------------------------

    story = []

    story.append(
        Paragraph(
            "AI TRAFFIC ENFORCEMENT",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Electronic Traffic Violation Challan",
            subtitle_style,
        )
    )

    # --------------------------------------------------------
    # CHALLAN INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Challan Information",
            heading_style,
        )
    )

    challan_data = [
        ["Challan ID", str(challan_id)],
        ["Date & Time", timestamp.strftime("%d-%m-%Y %I:%M:%S %p")],
        ["Status", "Pending Payment"],
    ]

    challan_table = Table(
        challan_data,
        colWidths=[55 * mm, 105 * mm],
    )

    challan_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F0FE")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(challan_table)
    story.append(Spacer(1, 10))

    # --------------------------------------------------------
    # VEHICLE INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Vehicle & Owner Information",
            heading_style,
        )
    )

    vehicle_data = [
        ["Owner Name", owner_name],
        ["Vehicle Number", number_plate],
        ["Vehicle Type", vehicle_type],
        ["Vehicle ID", vehicle_id],
        ["Contact", phone],
    ]

    vehicle_table = Table(
        vehicle_data,
        colWidths=[55 * mm, 105 * mm],
    )

    vehicle_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F0FE")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(vehicle_table)
    story.append(Spacer(1, 10))

    # --------------------------------------------------------
    # VIOLATION INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Violation Details",
            heading_style,
        )
    )

    violation_data = [
        ["Detected Violation", violation],
        ["Fine Amount", f"₹ {fine:,.2f}"],
        ["Detection Method", "AI-Based Traffic Analysis"],
    ]

    if ai_confidence is not None:
        violation_data.append(
            [
                "AI Confidence",
                f"{float(ai_confidence) * 100:.2f}%",
            ]
        )

    violation_table = Table(
        violation_data,
        colWidths=[55 * mm, 105 * mm],
    )

    violation_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#FFF3CD"),
                ),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(violation_table)
    story.append(Spacer(1, 15))

    # --------------------------------------------------------
    # TOTAL FINE
    # --------------------------------------------------------

    total_data = [
        [
            Paragraph("<b>TOTAL FINE</b>", normal_style),
            Paragraph(
                f"<b>₹ {fine:,.2f}</b>",
                normal_style,
            ),
        ]
    ]

    total_table = Table(
        total_data,
        colWidths=[110 * mm, 50 * mm],
    )

    total_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F8D7DA"),
                ),
                ("BOX", (0, 0), (-1, -1), 1, colors.grey),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )

    story.append(total_table)
    story.append(Spacer(1, 20))

    # --------------------------------------------------------
    # FOOTER NOTE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "This electronic challan was generated by the "
            "AI Traffic Enforcement System.",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "Please retain this document for your records.",
            subtitle_style,
        )
    )

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    document.build(story)

    return pdf_path


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    demo_vehicle = {
        "owner_name": "Demo User 1",
        "number_plate": "TS09PA3330",
        "vehicle_type": "Motorcycle",
        "vehicle_id": "VH001",
        "phone": "9000000001",
    }

    pdf_file = generate_challan_pdf(
        challan_id="CHL-DEMO-001",
        vehicle=demo_vehicle,
        violation="No Helmet",
        fine=200,
        ai_confidence=0.95,
    )

    print("\n=============================================")
    print("E-CHALLAN GENERATED")
    print("=============================================")
    print(f"PDF: {pdf_file}")