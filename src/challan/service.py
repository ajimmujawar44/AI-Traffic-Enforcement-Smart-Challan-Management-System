from src.database.models import (
    find_vehicle,
    get_violation_fine,
    create_challan,
)

from src.challan.generator import generate_challan_pdf


def create_e_challan(vehicle_reg, violation, ai_confidence=None):
    """
    Create a complete e-challan.

    Flow:
        Vehicle
            ↓
        Find Vehicle
            ↓
        Find Fine
            ↓
        Create Challan in Database
            ↓
        Generate PDF
    """

    # ============================================================
    # 1. FIND VEHICLE
    # ============================================================

    vehicle = find_vehicle(vehicle_reg)

    if not vehicle:
        raise ValueError(
            f"Vehicle '{vehicle_reg}' was not found in the database."
        )

    # ============================================================
    # 2. FIND FINE
    # ============================================================

    fine = get_violation_fine(violation)

    if fine is None:
        raise ValueError(
            f"No fine configured for violation: {violation}"
        )

    # ============================================================
    # 3. CREATE CHALLAN IN DATABASE
    # ============================================================

    challan = create_challan(
        vehicle_reg=vehicle_reg,
        violation_name=violation,
        fine=fine,
    )

    # create_challan() returns a dictionary
    challan_id = challan["challan_id"]

    # ============================================================
    # 4. PREPARE VEHICLE DATA FOR PDF
    # ============================================================

    # Database field names:
    # vehicle_reg → PDF expects number_plate
    # mobile      → PDF expects phone

    pdf_vehicle = {
        "owner_name": vehicle["owner_name"],
        "number_plate": vehicle["vehicle_reg"],
        "vehicle_type": vehicle["vehicle_type"],
        "vehicle_id": vehicle["vehicle_id"],
        "phone": vehicle["mobile"],
    }

    # ============================================================
    # 5. GENERATE PDF E-CHALLAN
    # ============================================================

    pdf_path = generate_challan_pdf(
        challan_id=challan_id,
        vehicle=pdf_vehicle,
        violation=violation,
        fine=fine,
        ai_confidence=ai_confidence,
    )

    # ============================================================
    # 6. RETURN COMPLETE RESULT
    # ============================================================

    return {
        "challan_id": challan_id,
        "vehicle": vehicle,
        "violation": violation,
        "fine": fine,
        "pdf_path": str(pdf_path),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = create_e_challan(
        vehicle_reg="TS09PA3330",
        violation="No Helmet",
        ai_confidence=0.95,
    )

    print("\n=============================================")
    print("E-CHALLAN SERVICE TEST")
    print("=============================================")

    print(f"Challan ID : {result['challan_id']}")
    print(f"Vehicle    : {result['vehicle']['vehicle_reg']}")
    print(f"Owner      : {result['vehicle']['owner_name']}")
    print(f"Violation  : {result['violation']}")
    print(f"Fine       : ₹{result['fine']}")
    print(f"PDF        : {result['pdf_path']}")

    print("=============================================")
    print("TEST COMPLETED")
    print("=============================================")