"""Serve only generated public profile-photo filenames."""
import mimetypes
import re

from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET


PHOTO_FILENAME = re.compile(r"^[a-f0-9]{32}\.(png|jpg|jpeg|webp)$", re.I)


@require_GET
def profile_photo_media(request, user_id, filename):
    if not PHOTO_FILENAME.fullmatch(filename):
        raise Http404("Profile photo not found")
    name = f"profile_photos/user_{user_id}/{filename}"
    if not default_storage.exists(name):
        raise Http404("Profile photo not found")
    content_type, _ = mimetypes.guess_type(filename)
    return FileResponse(default_storage.open(name, "rb"), content_type=content_type)
