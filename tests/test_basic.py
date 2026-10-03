import os

from src.database.models import (
    find_vehicle,
    get_violation_fine,
    generate_challan_id,
)

from src.utils.image_utils import SUPPORTED_EXTENSIONS


# ============================================================
# VEHICLE TEST
# ============================================================

def test_find_demo_vehicle():

    vehicle = find_vehicle("TS09PA3330")

    assert vehicle is not None
    assert vehicle["vehicle_reg"] == "TS09PA3330"


# ============================================================
# UNKNOWN VEHICLE TEST
# ============================================================

def test_unknown_vehicle():

    vehicle = find_vehicle("XX00XX0000")

    assert vehicle is None


# ============================================================
# FINE TEST
# ============================================================

def test_violation_fine():

    fine = get_violation_fine("No Helmet")

    assert fine == 200


# ============================================================
# CHALLAN ID TEST
# ============================================================

def test_challan_id():

    challan_id = generate_challan_id()

    assert challan_id.startswith("CHL-")


# ============================================================
# IMAGE FORMAT TEST
# ============================================================

def test_supported_image_formats():

    assert ".jpg" in SUPPORTED_EXTENSIONS
    assert ".jpeg" in SUPPORTED_EXTENSIONS
    assert ".png" in SUPPORTED_EXTENSIONS
    assert ".webp" in SUPPORTED_EXTENSIONS