"""Supabase Storage service for file uploads."""

import uuid

from app.config.settings import get_settings


class StorageService:
    """Service for uploading files to Supabase Storage."""

    def __init__(self) -> None:
        """Initialize the storage service."""
        self._client = None

    def _get_client(self):
        """Lazily initialize Supabase client.

        Returns:
            Supabase client or None if not configured.
        """
        if self._client is None:
            settings = get_settings()
            if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
                try:
                    from supabase import create_client

                    self._client = create_client(
                        settings.SUPABASE_URL,
                        settings.SUPABASE_SERVICE_KEY,
                    )
                    print("INFO [StorageService]: Supabase client initialized")
                except Exception as e:
                    print(f"ERROR [StorageService]: Failed to initialize Supabase client: {e}")
                    self._client = None
        return self._client

    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/pdf",
        folder: str = "audits",
    ) -> str:
        """Upload file to Supabase Storage and return public URL.

        Args:
            file_content: The file content as bytes.
            file_name: Original filename.
            content_type: MIME type of the file.
            folder: Folder path within the bucket.

        Returns:
            Public HTTPS URL of the uploaded file.

        Raises:
            RuntimeError: If Supabase Storage is not configured.
            Exception: If upload fails.
        """
        client = self._get_client()
        if not client:
            raise RuntimeError("Supabase Storage not configured")

        # Generate unique path to avoid collisions
        unique_id = uuid.uuid4().hex
        safe_filename = file_name.replace(" ", "_")
        unique_path = f"{folder}/{unique_id}_{safe_filename}"

        settings = get_settings()
        bucket = settings.SUPABASE_STORAGE_BUCKET

        print(f"INFO [StorageService]: Uploading file to bucket '{bucket}' at path '{unique_path}'")

        try:
            # Upload to storage
            client.storage.from_(bucket).upload(
                unique_path,
                file_content,
                {"content-type": content_type},
            )

            # Get public URL
            url = client.storage.from_(bucket).get_public_url(unique_path)
            print(f"INFO [StorageService]: Upload successful, URL: {url}")

            return url

        except Exception as e:
            print(f"ERROR [StorageService]: Upload failed: {e}")
            raise

    def delete_file(self, file_url: str) -> bool:
        """Delete file from Supabase Storage.

        Args:
            file_url: The public URL of the file to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        client = self._get_client()
        if not client:
            print("WARN [StorageService]: Cannot delete file - Supabase not configured")
            return False

        settings = get_settings()
        bucket = settings.SUPABASE_STORAGE_BUCKET

        # Extract path from URL
        # URL format: https://<project>.supabase.co/storage/v1/object/public/<bucket>/<path>
        try:
            # Find the bucket name in the URL and extract the path after it
            bucket_marker = f"/public/{bucket}/"
            if bucket_marker in file_url:
                path = file_url.split(bucket_marker)[1]
            else:
                print(f"WARN [StorageService]: Could not extract path from URL: {file_url}")
                return False

            print(f"INFO [StorageService]: Deleting file at path '{path}'")
            client.storage.from_(bucket).remove([path])
            return True

        except Exception as e:
            print(f"ERROR [StorageService]: Delete failed: {e}")
            return False

    def is_configured(self) -> bool:
        """Check if Supabase Storage is properly configured.

        Returns:
            True if SUPABASE_URL and SUPABASE_SERVICE_KEY are set.
        """
        settings = get_settings()
        return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)


# Singleton instance
storage_service = StorageService()
