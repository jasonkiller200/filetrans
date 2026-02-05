import os
import json
import uuid
import shutil
from typing import List, Dict
from models import FileInfo
from werkzeug.security import generate_password_hash, check_password_hash

class FileService:
    """Handles file-related business logic using metadata for filenames."""

    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        self._metadata_path = os.path.join(self.upload_folder, 'metadata.json')

    def _load_metadata(self) -> Dict[str, Dict]:
        """Loads the metadata from the JSON file."""
        if not os.path.exists(self._metadata_path):
            return {}
        try:
            with open(self._metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Backward compatibility: convert old string values to dict
                new_data = {}
                for k, v in data.items():
                    if isinstance(v, str):
                        new_data[k] = {'original_name': v, 'password_hash': None}
                    else:
                        new_data[k] = v
                return new_data
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_metadata(self, metadata: Dict[str, Dict]):
        """Saves the metadata to the JSON file."""
        with open(self._metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def get_all_files(self, sort_by: str = 'name', order: str = 'asc') -> List[FileInfo]:
        """
        Scans for files based on metadata and returns a list of FileInfo objects.
        Args:
            sort_by: Field to sort by ('name', 'size', 'date').
            order: Sort order ('asc', 'desc').
        """
        metadata = self._load_metadata()
        files = []
        
        # We iterate through a copy of the items because we might modify the dict
        for stored_name, meta_data in list(metadata.items()):
            path = os.path.join(self.upload_folder, stored_name)
            if os.path.exists(path):
                files.append(FileInfo(
                    original_name=meta_data['original_name'],
                    stored_name=stored_name,
                    path=path,
                    has_password=bool(meta_data.get('password_hash'))
                ))
            else:
                # If file is missing on disk, remove it from metadata
                # (This is a self-healing mechanism)
                del metadata[stored_name]
                self._save_metadata(metadata)

        # Content of values to be sorted
        reverse = (order == 'desc')
        
        if sort_by == 'size':
            files.sort(key=lambda f: f.size_in_bytes, reverse=reverse)
        elif sort_by == 'date':
            files.sort(key=lambda f: os.path.getmtime(f.path), reverse=reverse)
        else: # default to name
            files.sort(key=lambda f: f.original_name.lower(), reverse=reverse)
            
        return files

    def save_file(self, file_storage, password: str = None) -> FileInfo:
        """
        Saves an uploaded file with a unique name and updates metadata.

        Args:
            file_storage: The file object from the request.
            password: Optional password for file protection.

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

        # Hash password if provided
        password_hash = generate_password_hash(password) if password else None

        # Update metadata
        metadata = self._load_metadata()
        metadata[stored_name] = {
            'original_name': original_name,
            'password_hash': password_hash
        }
        self._save_metadata(metadata)

        return FileInfo(
            original_name=original_name,
            stored_name=stored_name,
            path=save_path,
            has_password=bool(password_hash)
        )

    def get_file_path(self, stored_name: str) -> str:
        """Returns the full path to a file in the upload folder."""
        # This function now expects the unique stored_name
        return os.path.join(self.upload_folder, stored_name)

    def get_original_filename(self, stored_name: str) -> str:
        """Retrieves the original filename from metadata."""
        metadata = self._load_metadata()
        meta_data = metadata.get(stored_name)
        if isinstance(meta_data, dict):
            return meta_data.get('original_name')
        return meta_data # Fallback if it's a string (though _load_metadata handles this, safety check)

    def verify_password(self, stored_name: str, password: str) -> bool:
        """
        Verifies the password for a file.
        Returns True if password is correct or if Admin Master Password is used.
        """
        metadata = self._load_metadata()
        meta_data = metadata.get(stored_name)
        if not meta_data or not isinstance(meta_data, dict):
            return False # Should not happen if file exists
        
        stored_hash = meta_data.get('password_hash')
        
        # If no password set, always allow (or should we return True? Logic dictates this checks IF protected)
        # But this function is called when we know it is protected.
        if not stored_hash:
            return True 
            
        # Admin Rescue Mechanism
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if admin_password and password == admin_password:
            return True
            
        return check_password_hash(stored_hash, password)

    def delete_file(self, stored_name: str):
        """
        Deletes a file from the filesystem and its corresponding metadata entry.
        """
        # Remove from metadata
        metadata = self._load_metadata()
        meta_data = metadata.pop(stored_name, None)
        self._save_metadata(metadata)
        
        original_name = None
        if meta_data:
            if isinstance(meta_data, dict):
                original_name = meta_data.get('original_name')
            else:
                original_name = meta_data

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
                    metadata[stored_name] = {'original_name': original_name, 'password_hash': meta_data.get('password_hash') if isinstance(meta_data, dict) else None}
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
