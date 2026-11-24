"""Safe image upload + image URL helper."""
import os
import re
import uuid

from flask import current_app, url_for


def _looks_like_image(head):
    return (
        head.startswith(b"\xff\xd8\xff")                       # JPEG
        or head.startswith(b"\x89PNG\r\n\x1a\n")                # PNG
        or (head[:4] == b"RIFF" and head[8:12] == b"WEBP")      # WEBP
    )


def save_image(file):
    """Returns (filename, error). (None, None) means no file was chosen."""
    if not file or not file.filename:
        return None, None
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return None, "Only JPG, PNG or WEBP images are allowed."
    head = file.stream.read(16)
    file.stream.seek(0)
    if not _looks_like_image(head):
        return None, "That file is not a real image."
    name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], name))
    return name, None


def delete_image(name):
    """Deletes only files this app uploaded (random names). Starter photos are kept."""
    if name and re.fullmatch(r"[0-9a-f]{32}\.(jpg|jpeg|png|webp)", name):
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
        if os.path.isfile(path):
            os.remove(path)


def image_url(name):
    if name:
        return url_for("static", filename="uploads/foods/" + name)
    return url_for("static", filename="images/placeholder.svg")
