import os
from pathlib import Path
from platformdirs import user_cache_path

CACHE_ROOT = user_cache_path("lyricutils")
USE_LOCAL_WORKSPACE = os.environ.get("LYRICUTILS_DEV_MODE") == "1"
if USE_LOCAL_WORKSPACE:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    CACHE_ROOT = PROJECT_ROOT / "cache"
