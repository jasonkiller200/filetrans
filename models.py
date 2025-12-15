import os
import math

class FileInfo:
    """Represents information about a single file."""
    def __init__(self, original_name: str, stored_name: str, path: str):
        self.original_name = original_name
        self.stored_name = stored_name
        self.path = path
        try:
            self.size_in_bytes = os.path.getsize(path)
        except FileNotFoundError:
            self.size_in_bytes = 0

    @property
    def formatted_size(self) -> str:
        """Returns the file size in a human-readable format (KB, MB, GB)."""
        if self.size_in_bytes == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        # Determine the appropriate unit
        # Add a check for size_in_bytes > 0 to avoid math domain error with log(0) or log(1)
        if self.size_in_bytes <= 0:
            return "0 B"
        i = int(math.floor(math.log(self.size_in_bytes, 1024)))
        # Format the size
        p = math.pow(1024, i)
        s = round(self.size_in_bytes / p, 2)
        return f"{s} {size_name[i]}"

    def __repr__(self):
        return f"<FileInfo(original_name='{self.original_name}', size='{self.formatted_size}')>"

