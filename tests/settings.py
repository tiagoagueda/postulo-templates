"""Settings for running the plugin's tests inside Postulo.

Postulo's own test settings add a throwaway app that only exists in Postulo's repository,
so a plugin cannot borrow them as they are. These are the same settings without it: an
in-memory database, temporary media and static directories, mail kept in memory.
"""

import tempfile

from postulo.config.settings.base import *  # noqa: F403

SECRET_KEY = "test-key-not-secret"  # noqa: S105
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
MAILERS = {"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}}

MEDIA_ROOT = tempfile.mkdtemp(prefix="postulo-templates-media-")
STATIC_ROOT = tempfile.mkdtemp(prefix="postulo-templates-static-")
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}
