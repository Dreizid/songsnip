import hashlib
from pathlib import Path


def calculate_file_hash(file_path: Path | str, chunk_size: int = 65536) -> str:
    """
    Computes a unique SHA-256 fingreprint based on the file's content.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Cannot calculate hash. File does not exist: {file_path}"
        )

    hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        chunk = f.read(chunk_size)

        while chunk:
            hasher.update(chunk)
            chunk = f.read(chunk_size)

    return hasher.hexdigest()
