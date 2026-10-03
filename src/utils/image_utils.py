from pathlib import Path

from PIL import Image


# ============================================================
# SUPPORTED IMAGE FORMATS
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# ============================================================
# VALIDATE IMAGE
# ============================================================

def validate_image(image_path):
    """
    Validate that the given file exists and is a supported image.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format: {image_path.suffix}"
        )

    try:
        with Image.open(image_path) as image:
            image.verify()

    except Exception as exc:
        raise ValueError(
            f"Invalid or corrupted image: {image_path}"
        ) from exc

    return True


# ============================================================
# GET IMAGE INFORMATION
# ============================================================

def get_image_info(image_path):
    """
    Return basic image information.
    """

    validate_image(image_path)

    with Image.open(image_path) as image:
        return {
            "filename": Path(image_path).name,
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
        }


# ============================================================
# RESIZE IMAGE
# ============================================================

def resize_image(
    image_path,
    output_path,
    max_width=1280,
    max_height=1280,
):
    """
    Resize an image while maintaining its aspect ratio.
    """

    validate_image(image_path)

    image_path = Path(image_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with Image.open(image_path) as image:

        # Convert images with transparency to RGB
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")

        image.thumbnail(
            (max_width, max_height),
            Image.Resampling.LANCZOS,
        )

        image.save(
            output_path,
            quality=90,
            optimize=True,
        )

    return output_path


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n=============================================")
    print("IMAGE UTILS TEST")
    print("=============================================")

    print("Supported formats:")

    for extension in sorted(SUPPORTED_EXTENSIONS):
        print(f"  ✓ {extension}")

    print("\nImage utilities loaded successfully.")

    print("=============================================")
    print("TEST COMPLETED")
    print("=============================================")