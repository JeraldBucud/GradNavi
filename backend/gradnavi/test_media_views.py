"""Production-style profile photo routing regression tests."""
import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings


class ProfilePhotoMediaTests(SimpleTestCase):
    def test_existing_photo_is_retrievable_with_debug_disabled(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root) / "profile_photos" / "user_1"
            directory.mkdir(parents=True)
            filename = "a" * 32 + ".png"
            (directory / filename).write_bytes(b"image-test")
            with override_settings(DEBUG=False, MEDIA_ROOT=root):
                response = self.client.get(f"/media/profile_photos/user_1/{filename}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "image/png")
                self.assertEqual(b"".join(response.streaming_content), b"image-test")

    def test_missing_photo_is_404(self):
        with tempfile.TemporaryDirectory() as root:
            with override_settings(DEBUG=False, MEDIA_ROOT=root):
                response = self.client.get("/media/profile_photos/user_1/" + "a" * 32 + ".png")
                self.assertEqual(response.status_code, 404)

    def test_non_generated_filename_is_404(self):
        with override_settings(DEBUG=False):
            response = self.client.get("/media/profile_photos/user_1/settings.py")
            self.assertEqual(response.status_code, 404)

    def test_unrelated_media_path_is_not_exposed(self):
        with override_settings(DEBUG=False):
            response = self.client.get("/media/private.txt")
            self.assertEqual(response.status_code, 404)
