import sqlite3
from pathlib import Path


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

# Project root:
# AI-Traffic-Enforcement/
BASE_DIR = Path(__file__).resolve().parents[2]

# Database will be created automatically here:
DATABASE_PATH = BASE_DIR / "traffic.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Create and return a SQLite database connection.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():
    """
    Create all required tables if they do not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # -----------------------------------------------------
    # VEHICLES / OWNERS TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_name TEXT NOT NULL,
            vehicle_reg TEXT NOT NULL UNIQUE,
            vehicle_type TEXT,
            vehicle_id TEXT,
            mobile TEXT
        )
        """
    )

    # -----------------------------------------------------
    # VIOLATIONS TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            violation_name TEXT NOT NULL UNIQUE,
            fine INTEGER NOT NULL
        )
        """
    )

    # -----------------------------------------------------
    # CHALLANS TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS challans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challan_id TEXT NOT NULL UNIQUE,
            vehicle_reg TEXT,
            violation_name TEXT,
            fine INTEGER,
            detected_at TEXT,
            status TEXT DEFAULT 'UNPAID'
        )
        """
    )

    # -----------------------------------------------------
    # VIOLATION HISTORY TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS violation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_reg TEXT,
            violation_name TEXT,
            fine INTEGER,
            detected_at TEXT
        )
        """
    )

    # -----------------------------------------------------
    # DEFAULT VIOLATION DATA
    # -----------------------------------------------------

    violations = [
        ("Triple Ride", 1000),
        ("No Parking", 100),
        ("No Helmet", 200),
        ("No Seatbelt", 1000),
        ("Overspeed", 1000),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO violations
        (
            violation_name,
            fine
        )
        VALUES (?, ?)
        """,
        violations
    )

    # -----------------------------------------------------
    # DEMO VEHICLE DATA
    # -----------------------------------------------------

    demo_vehicles = [
    (
        "Demo User 1",
        "TS09PA3330",
        "Car",
        "VH001",
        "9000000001",
    ),
    (
        "Demo User 2",
        "AP28R8104",
        "Motorcycle",
        "VH002",
        "9000000002",
    ),
    (
        "Demo User 3",
        "GR023B4401",
        "Motorcycle",
        "VH003",
        "9000000003",
    ),
    (
        "Demo User 4",
        "TS22G5744",
        "Car",
        "VH004",
        "9000000004",
    ),
    (
        "Demo User 5",
        "MH43BA2518",
        "Car",
        "VH005",
        "9000000005",
    ),
    (
        "Demo User 6",
        "TS10EX2850",
        "Scooter",
        "VH006",
        "9000000006",
    ),
]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO vehicles
        (
            owner_name,
            vehicle_reg,
            vehicle_type,
            vehicle_id,
            mobile
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        demo_vehicles
    )

    connection.commit()

    connection.close()


# =========================================================
# NORMALIZE NUMBER PLATE
# =========================================================

def normalize_plate(plate):
    """
    Convert vehicle registration into a standard format.

    Example:
        TS 09 PA 3330
        TS-09-PA-3330

    becomes:

        TS09PA3330
    """

    if not plate:
        return ""

    return "".join(
        character
        for character in str(plate).upper()
        if character.isalnum()
    )


# =========================================================
# GET FINE
# =========================================================

def get_fine(violation):
    """
    Return the fine amount for a violation.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT fine
        FROM violations
        WHERE LOWER(violation_name) = LOWER(?)
        """,
        (violation,)
    )

    row = cursor.fetchone()

    connection.close()

    if row:
        return row["fine"]

    return 0


# =========================================================
# GET VEHICLE
# =========================================================

def get_vehicle(number_plate):
    """
    Find a registered vehicle using its number plate.
    """

    detected_plate = normalize_plate(number_plate)

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
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

        database_plate = normalize_plate(
            vehicle["vehicle_reg"]
        )

        if database_plate == detected_plate:

            return {
                "owner_name": vehicle["owner_name"],
                "vehicle_reg": vehicle["vehicle_reg"],
                "vehicle_type": vehicle["vehicle_type"],
                "vehicle_id": vehicle["vehicle_id"],
                "mobile": vehicle["mobile"],
            }

    return None


# =========================================================
# GET ALL VEHICLES
# =========================================================

def get_all_vehicles():
    """
    Return all registered demo vehicles.
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
        ORDER BY id
        """
    )

    vehicles = cursor.fetchall()

    connection.close()

    return [dict(vehicle) for vehicle in vehicles]


# =========================================================
# ADD VIOLATION HISTORY
# =========================================================

def add_violation_history(
    vehicle_reg,
    violation_name,
    fine,
    detected_at
):
    """
    Save a detected violation into history.
    """

    connection = get_connection()

    cursor = connection.cursor()

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
            detected_at
        )
    )

    connection.commit()

    connection.close()


# =========================================================
# GET VIOLATION HISTORY
# =========================================================

def get_violation_history(vehicle_reg=None):
    """
    Return violation history.

    If vehicle_reg is provided,
    return history for that vehicle only.
    """

    connection = get_connection()

    cursor = connection.cursor()

    if vehicle_reg:

        cursor.execute(
            """
            SELECT
                id,
                vehicle_reg,
                violation_name,
                fine,
                detected_at
            FROM violation_history
            WHERE vehicle_reg = ?
            ORDER BY id DESC
            """,
            (vehicle_reg,)
        )

    else:

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

    history = cursor.fetchall()

    connection.close()

    return [dict(row) for row in history]


# =========================================================
# CREATE CHALLAN
# =========================================================

def save_challan(
    challan_id,
    vehicle_reg,
    violation_name,
    fine,
    detected_at
):
    """
    Save a generated challan.
    """

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
            "UNPAID"
        )
    )

    connection.commit()

    connection.close()


# =========================================================
# INITIALIZE DATABASE WHEN MODULE IS USED
# =========================================================

initialize_database()