import os
import json
import uuid
import shutil
from typing import List, Dict
from models import FileInfo

class FileService:
    """Handles file-related business logic using metadata for filenames."""

    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        self._metadata_path = os.path.join(self.upload_folder, 'metadata.json')

    def _load_metadata(self) -> Dict[str, str]:
        """Loads the metadata from the JSON file."""
        if not os.path.exists(self._metadata_path):
            return {}
        try:
            with open(self._metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_metadata(self, metadata: Dict[str, str]):
        """Saves the metadata to the JSON file."""
        with open(self._metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def get_all_files(self) -> List[FileInfo]:
        """
        Scans for files based on metadata and returns a list of FileInfo objects.
        """
        metadata = self._load_metadata()
        files = []
        
        # We iterate through a copy of the items because we might modify the dict
        for stored_name, original_name in list(metadata.items()):
            path = os.path.join(self.upload_folder, stored_name)
            if os.path.exists(path):
                files.append(FileInfo(
                    original_name=original_name,
                    stored_name=stored_name,
                    path=path
                ))
            else:
                # If file is missing on disk, remove it from metadata
                # (This is a self-healing mechanism)
                del metadata[stored_name]
                self._save_metadata(metadata)

        # Sort files by original name
        files.sort(key=lambda f: f.original_name.lower())
        return files

    def save_file(self, file_storage) -> FileInfo:
        """
        Saves an uploaded file with a unique name and updates metadata.

        Args:
            file_storage: The file object from the request.

        Returns:
            A FileInfo object for the newly saved file.
        """
        original_name = file_storage.filename
        if not original_name:
            raise ValueError("No filename provided.")

        # Create a unique filename using UUID, preserving the extension
        file_extension = os.path.splitext(original_name)[1]
        stored_name = f"{uuid.uuid4()}{file_extension}"
        
        save_path = os.path.join(self.upload_folder, stored_name)
        file_storage.save(save_path)

        # Update metadata
        metadata = self._load_metadata()
        metadata[stored_name] = original_name
        self._save_metadata(metadata)

        return FileInfo(
            original_name=original_name,
            stored_name=stored_name,
            path=save_path
        )

    def get_file_path(self, stored_name: str) -> str:
        """Returns the full path to a file in the upload folder."""
        # This function now expects the unique stored_name
        return os.path.join(self.upload_folder, stored_name)

    def get_original_filename(self, stored_name: str) -> str:
        """Retrieves the original filename from metadata."""
        metadata = self._load_metadata()
        return metadata.get(stored_name)

    def delete_file(self, stored_name: str):
        """
        Deletes a file from the filesystem and its corresponding metadata entry.
        """
        # Remove from metadata
        metadata = self._load_metadata()
        original_name = metadata.pop(stored_name, None)
        self._save_metadata(metadata)

        # Delete file from disk
        file_path = self.get_file_path(stored_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                # Handle cases where the file might be in use or other permission errors
                print(f"Error deleting file {file_path}: {e}")
                # Optionally, re-add metadata if file deletion fails
                if original_name:
                    metadata[stored_name] = original_name
                    self._save_metadata(metadata)
                raise # Re-raise the exception to be handled by the controller
        
        return original_name # Return original name for flash message

    def transfer_to_mps(self, file_info: FileInfo, destination_folder: str):
        """
        Transfers the file to the specified MPS network folder.
        """
        # Ensure destination folder exists
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder) # Create if it doesn't exist

        # Construct full destination path with original filename
        destination_path = os.path.join(destination_folder, file_info.original_name)
        
        # Move the file
        shutil.move(file_info.path, destination_path)
