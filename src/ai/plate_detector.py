import re


# ============================================================
# NUMBER PLATE UTILITIES
# ============================================================

def normalize_plate(number_plate):
    """
    Normalize an Indian vehicle registration number.

    Example:
        'ts 09 pa 3330' -> 'TS09PA3330'
    """

    if not number_plate:
        return ""

    plate = str(number_plate).upper()

    # Remove spaces, hyphens and other non-alphanumeric characters
    plate = re.sub(r"[^A-Z0-9]", "", plate)

    return plate


def is_valid_plate(number_plate):
    """
    Basic validation for an Indian-style vehicle plate.

    Examples:
        TS09PA3330 -> True
        MH12AB1234 -> True
    """

    plate = normalize_plate(number_plate)

    pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}$"

    return bool(re.fullmatch(pattern, plate))


def extract_plate_from_text(text):
    """
    Try to find a vehicle registration number
    inside a text response.
    """

    if not text:
        return None

    text = str(text).upper()

    pattern = r"\b[A-Z]{2}[\s-]?[0-9]{1,2}[\s-]?[A-Z]{1,3}[\s-]?[0-9]{1,4}\b"

    match = re.search(pattern, text)

    if not match:
        return None

    return normalize_plate(match.group())


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=============================================")
    print("NUMBER PLATE DETECTOR TEST")
    print("=============================================")

    test_plates = [
        "TS 09 PA 3330",
        "MH-12-AB-1234",
        "KA01AA5678",
        "TS10ED8176",
        "INVALID",
    ]

    for plate in test_plates:

        normalized = normalize_plate(plate)
        valid = is_valid_plate(plate)

        print(
            f"{plate:<18} -> "
            f"{normalized:<15} | "
            f"Valid: {valid}"
        )

    print("\nText extraction test:")

    text = "Detected vehicle number is TS 10 ED 8176."

    extracted = extract_plate_from_text(text)

    print(f"Input     : {text}")
    print(f"Extracted : {extracted}")

    print("=============================================")
    print("TEST COMPLETED")
    print("=============================================")