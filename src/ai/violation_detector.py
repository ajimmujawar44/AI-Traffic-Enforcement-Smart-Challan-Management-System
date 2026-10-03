import os
import base64
import re

from dotenv import load_dotenv
from groq import Groq


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. "
        "Please add GROQ_API_KEY to your .env file."
    )

client = Groq(
    api_key=GROQ_API_KEY
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "qwen/qwen3.8-27b",
)

ALLOWED_VIOLATIONS = [
    "Triple Ride",
    "No Parking",
    "No Helmet",
    "No Seatbelt",
    "Overspeed",
]


# =========================================================
# IMAGE ENCODING
# =========================================================

def encode_image(image_path: str) -> str:
    """
    Convert an image file into a Base64 string.
    """

    if not os.path.exists(image_path):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    with open(
        image_path,
        "rb",
    ) as file:

        return base64.b64encode(
            file.read()
        ).decode("utf-8")


# =========================================================
# CLEAN MODEL RESPONSE
# =========================================================

def clean_response(response: str) -> str:
    """
    Remove thinking tags and unnecessary formatting
    from the model response.
    """

    if not response:
        return ""

    response = response.strip()

    response_lower = response.lower()

    # -----------------------------------------------------
    # Remove <think>...</think>
    # -----------------------------------------------------

    if "<think>" in response_lower:

        start = response_lower.find(
            "<think>"
        )

        end = response_lower.find(
            "</think>"
        )

        if end != -1:

            response = response[
                end + len("</think>"):
            ]

        else:

            response = response[
                start + len("<think>"):
            ]

    # -----------------------------------------------------
    # Remove markdown formatting
    # -----------------------------------------------------

    response = response.replace(
        "`",
        "",
    )

    response = response.replace(
        "*",
        "",
    )

    response = response.replace(
        "#",
        "",
    )

    return response.strip()


# =========================================================
# NORMALIZE NUMBER PLATE
# =========================================================

def normalize_plate(
    plate: str,
) -> str:
    """
    Convert a vehicle number plate into a
    comparable format.

    Example:
        TS09 PA 3330 -> TS09PA3330
    """

    if not plate:
        return ""

    return "".join(
        character
        for character in str(plate).upper()
        if character.isalnum()
    )


# =========================================================
# DETECT TRAFFIC VIOLATION
# =========================================================

def detect_violation(
    image_path: str,
) -> str:
    """
    Analyze a traffic image and identify one
    supported traffic violation.
    """

    image_base64 = encode_image(
        image_path
    )

    prompt = """
You are an AI traffic enforcement assistant.

Analyze the provided traffic image.

Detect ONE traffic violation only when it is
clearly visible.

Allowed violations:

1. Triple Ride
   - More than two people riding on a two-wheeler.

2. No Parking
   - A vehicle is parked in a location where
     parking is prohibited.

3. No Helmet
   - A motorcycle or scooter rider is riding
     without a helmet.

4. No Seatbelt
   - A driver or front-seat occupant in a car
     is visibly not wearing a seatbelt.

5. Overspeed
   - Only identify this violation when the image
     or available context provides sufficient
     evidence of speeding.
   - Do not assume overspeeding simply because
     a vehicle is present.

If none of these violations is clearly visible,
return:

No Violation

Return ONLY one of these exact values:

Triple Ride
No Parking
No Helmet
No Seatbelt
Overspeed
No Violation

Do not provide:
- reasoning
- explanation
- markdown
- <think> tags
- additional text
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=100,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                "data:image/jpeg;base64,"
                                f"{image_base64}"
                            ),
                        },
                    },
                ],
            }
        ],
    )

    result = response.choices[
        0
    ].message.content

    result = clean_response(
        result
    )

    result_lower = result.lower()

    # -----------------------------------------------------
    # Exact / partial matching
    # -----------------------------------------------------

    if "triple ride" in result_lower:

        return "Triple Ride"

    if "no parking" in result_lower:

        return "No Parking"

    if "no helmet" in result_lower:

        return "No Helmet"

    if "no seatbelt" in result_lower:

        return "No Seatbelt"

    if "no seat belt" in result_lower:

        return "No Seatbelt"

    if "overspeed" in result_lower:

        return "Overspeed"

    if "no violation" in result_lower:

        return "Unknown"

    # -----------------------------------------------------
    # Handle slight model variations
    # -----------------------------------------------------

    if "triple" in result_lower:

        return "Triple Ride"

    if "parking" in result_lower:

        return "No Parking"

    if "helmet" in result_lower:

        return "No Helmet"

    if "seatbelt" in result_lower:

        return "No Seatbelt"

    if "seat belt" in result_lower:

        return "No Seatbelt"

    if "overspeed" in result_lower:

        return "Overspeed"

    return "Unknown"


# =========================================================
# DETECT NUMBER PLATE
# =========================================================

def detect_number_plate(
    image_path: str,
) -> str:
    """
    Detect an Indian vehicle registration number
    from the image.
    """

    image_base64 = encode_image(
        image_path
    )

    prompt = """
You are an AI number plate detection assistant.

Analyze the provided traffic image.

Find the clearly visible vehicle registration number.

Return the vehicle number plate exactly.

Examples:

TS09PA3330
AP28R8104
GR023B4401
TS22G5744
MH43BA2518
TS10EX2850

The plate may contain spaces or hyphens.

Examples:

TS 09 PA 3330
AP 28 R 8104
MH-43-BA-2518
TS-10-EX-2850

Return ONLY the number plate.

Do not return:
- explanation
- reasoning
- markdown
- <think> tags
- "Number Plate:"
- additional text

If no clearly visible number plate exists, return:

Not Detected
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=100,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                "data:image/jpeg;base64,"
                                f"{image_base64}"
                            ),
                        },
                    },
                ],
            }
        ],
    )

    result = response.choices[
        0
    ].message.content

    result = clean_response(
        result
    )

    result = result.upper()

    # -----------------------------------------------------
    # Debug output
    # -----------------------------------------------------

    print(
        f"DEBUG - AI Plate Response: {result}"
    )

    # -----------------------------------------------------
    # Pattern 1
    #
    # Spaced / hyphenated plate
    #
    # TS 10 EX 2850
    # TS-10-EX-2850
    # -----------------------------------------------------

    matches = re.findall(
        r"\b[A-Z]{2}"
        r"[\s-]*"
        r"\d{1,2}"
        r"[\s-]*"
        r"[A-Z]{1,3}"
        r"[\s-]*"
        r"\d{3,4}\b",
        result,
    )

    if matches:

        plate = normalize_plate(
            matches[0]
        )

        print(
            f"DEBUG - Extracted Plate: {plate}"
        )

        return plate

    # -----------------------------------------------------
    # Pattern 2
    #
    # Compact plate
    #
    # TS10EX2850
    # -----------------------------------------------------

    matches = re.findall(
        r"\b[A-Z]{2}"
        r"\d{1,2}"
        r"[A-Z]{1,3}"
        r"\d{3,4}\b",
        result,
    )

    if matches:

        plate = normalize_plate(
            matches[0]
        )

        print(
            f"DEBUG - Extracted Plate: {plate}"
        )

        return plate

    # -----------------------------------------------------
    # Pattern 3
    #
    # Search inside a longer AI response
    # -----------------------------------------------------

    cleaned_result = re.sub(
        r"[^A-Z0-9]",
        "",
        result,
    )

    matches = re.findall(
        r"[A-Z]{2}"
        r"\d{1,2}"
        r"[A-Z]{1,3}"
        r"\d{3,4}",
        cleaned_result,
    )

    if matches:

        plate = normalize_plate(
            matches[0]
        )

        print(
            f"DEBUG - Extracted Plate: {plate}"
        )

        return plate

    print(
        "DEBUG - No valid number plate found."
    )

    return ""


# =========================================================
# VALIDATE VIOLATION
# =========================================================

def is_valid_violation(
    violation: str,
) -> bool:
    """
    Check whether the detected violation is supported.
    """

    return violation in ALLOWED_VIOLATIONS


# =========================================================
# MAIN AI ANALYSIS
# =========================================================

def analyze_traffic_image(
    image_path: str,
) -> dict:
    """
    Perform complete AI analysis:

    1. Detect violation
    2. Detect number plate
    3. Validate violation
    4. Return structured result
    """

    violation = detect_violation(
        image_path
    )

    number_plate = detect_number_plate(
        image_path
    )

    return {
        "violation": violation,
        "number_plate": number_plate,
        "valid_violation": is_valid_violation(
            violation
        ),
    }


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print(
        "\n" + "=" * 45
    )

    print(
        "AI TRAFFIC ENFORCEMENT"
    )

    print(
        "=" * 45
    )

    test_image = os.path.join(
        "sample_data",
        "images",
        "no_helmet.jpg",
    )

    if not os.path.exists(
        test_image
    ):

        print(
            f"\nImage not found:\n{test_image}"
        )

        print(
            "\nPut a test image inside:"
        )

        print(
            "sample_data/images/"
        )

        raise SystemExit

    print(
        "\n🔍 Detecting violation..."
    )

    violation = detect_violation(
        test_image
    )

    print(
        f"Violation: {violation}"
    )

    print(
        "\n🔍 Detecting number plate..."
    )

    number_plate = detect_number_plate(
        test_image
    )

    print(
        f"Number Plate: {number_plate}"
    )

    print(
        "\n" + "=" * 45
    )

    print(
        "ANALYSIS COMPLETE"
    )

    print(
        "=" * 45
    )