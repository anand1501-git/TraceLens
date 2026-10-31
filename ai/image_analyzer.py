from pathlib import Path
from ai.gemma_client import client, MODEL


def analyze_error_screenshot(image_path):
    image_path = Path(image_path)

    if not image_path.is_file():
        raise FileNotFoundError(
            f"Screenshot not found: {image_path}"
        )

    uploaded_image = client.files.upload(
        file=str(image_path)
    )

    prompt = """
    Analyze this programming error screenshot.

    Identify:
    1. The error message.
    2. The likely error type.
    3. The possible root cause.
    4. What information or code should be checked next.

    Be precise. If something cannot be determined
    from the screenshot, clearly say so.
    """

    response = client.models.generate_content(
        model=MODEL,
        contents=[uploaded_image, prompt]
    )

    return response.text