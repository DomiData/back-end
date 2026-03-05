import re


def secure_filename(filename: str) -> str:
    if not filename:
        return "export_data"
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", filename)

    return safe_name.strip("_") or "export_data"
