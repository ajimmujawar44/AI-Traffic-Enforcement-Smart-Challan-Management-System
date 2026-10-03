from datetime import datetime
import uuid

from .database import (
    get_connection,
    normalize_plate,
)


# =========================================================
# VEHICLE OPERATIONS
# =========================================================

def find_vehicle(number_plate):
    """
    Find a registered vehicle using its number plate.
    """

    plate = normalize_plate(number_plate)

    if not plate:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            owner_name,
            vehicle_reg,
            vehicle_type,
            vehicle_id,
            mobile
        FROM vehicles
        """
    )

    vehicles = cursor.fetchall()

    connection.close()

    for vehicle in vehicles:

        registered_plate = normalize_plate(
            vehicle["vehicle_reg"]
        )

        if registered_plate == plate:

            return dict(vehicle)

    return None


def get_all_vehicles():
    """
    Return all registered vehicles.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            owner_name,
            vehicle_reg,
            vehicle_type,
            vehicle_id,
            mobile
        FROM vehicles
        ORDER BY id DESC
        """
    )

    vehicles = cursor.fetchall()

    connection.close()

    return [dict(vehicle) for vehicle in vehicles]


# =========================================================
# VIOLATION OPERATIONS
# =========================================================

def get_violation_fine(violation_name):
    """
    Get fine amount for a specific violation.
    """

    if not violation_name:
        return 0

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT fine
        FROM violations
        WHERE LOWER(violation_name) = LOWER(?)
        """,
        (violation_name.strip(),)
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result["fine"]

    return 0


def get_all_violations():
    """
    Return all available traffic violations.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            violation_name,
            fine
        FROM violations
        ORDER BY id
        """
    )

    violations = cursor.fetchall()

    connection.close()

    return [dict(violation) for violation in violations]


# =========================================================
# VIOLATION HISTORY
# =========================================================

def save_violation(
    vehicle_reg,
    violation_name,
    fine,
):
    """
    Save a detected violation into history.
    """

    connection = get_connection()
    cursor = connection.cursor()

    detected_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        INSERT INTO violation_history
        (
            vehicle_reg,
            violation_name,
            fine,
            detected_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            vehicle_reg,
            violation_name,
            fine,
            detected_at,
        )
    )

    connection.commit()
    connection.close()

    return detected_at


def get_violation_history(vehicle_reg=None):
    """
    Get violation history.

    If vehicle_reg is provided,
    return history for that vehicle.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if vehicle_reg:

        plate = normalize_plate(vehicle_reg)

        cursor.execute(
            """
            SELECT
                id,
                vehicle_reg,
                violation_name,
                fine,
                detected_at
            FROM violation_history
            ORDER BY id DESC
            """
        )

        records = cursor.fetchall()

        connection.close()

        filtered_records = []

        for record in records:

            if normalize_plate(
                record["vehicle_reg"]
            ) == plate:

                filtered_records.append(
                    dict(record)
                )

        return filtered_records

    cursor.execute(
        """
        SELECT
            id,
            vehicle_reg,
            violation_name,
            fine,
            detected_at
        FROM violation_history
        ORDER BY id DESC
        """
    )

    records = cursor.fetchall()

    connection.close()

    return [dict(record) for record in records]


# =========================================================
# CHALLAN OPERATIONS
# =========================================================

def generate_challan_id():
    """
    Generate a unique challan ID.

    Example:
        CHL-2026-A1B2C3D4
    """

    unique_id = uuid.uuid4().hex[:8].upper()

    year = datetime.now().year

    return f"CHL-{year}-{unique_id}"


def create_challan(
    vehicle_reg,
    violation_name,
    fine,
):
    """
    Create and save a new challan.
    """

    challan_id = generate_challan_id()

    detected_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO challans
        (
            challan_id,
            vehicle_reg,
            violation_name,
            fine,
            detected_at,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            challan_id,
            vehicle_reg,
            violation_name,
            fine,
            detected_at,
            "UNPAID",
        )
    )

    connection.commit()
    connection.close()

    return {
        "challan_id": challan_id,
        "vehicle_reg": vehicle_reg,
        "violation_name": violation_name,
        "fine": fine,
        "detected_at": detected_at,
        "status": "UNPAID",
    }


def get_all_challans():
    """
    Return all generated challans.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            challan_id,
            vehicle_reg,
            violation_name,
            fine,
            detected_at,
            status
        FROM challans
        ORDER BY id DESC
        """
    )

    challans = cursor.fetchall()

    connection.close()

    return [dict(challan) for challan in challans]


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

def get_dashboard_statistics():
    """
    Return basic statistics for the dashboard.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # Total registered vehicles
    cursor.execute(
        "SELECT COUNT(*) AS count FROM vehicles"
    )

    total_vehicles = cursor.fetchone()["count"]

    # Total violations
    cursor.execute(
        "SELECT COUNT(*) AS count FROM violation_history"
    )

    total_violations = cursor.fetchone()["count"]

    # Total challans
    cursor.execute(
        "SELECT COUNT(*) AS count FROM challans"
    )

    total_challans = cursor.fetchone()["count"]

    # Total fines
    cursor.execute(
        """
        SELECT COALESCE(SUM(fine), 0) AS total
        FROM challans
        """
    )

    total_fines = cursor.fetchone()["total"]

    connection.close()

    return {
        "total_vehicles": total_vehicles,
        "total_violations": total_violations,
        "total_challans": total_challans,
        "total_fines": total_fines,
    }