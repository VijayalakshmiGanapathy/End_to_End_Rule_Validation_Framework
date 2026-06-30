from pathlib import Path

from app.core.paths import BatchPaths


class DownloadManager:
    """
    Returns the Selenium download folder for a batch.
    Folder creation is handled by BatchPaths.
    """

    @classmethod
    def get_batch_download_folder(
        cls,
        batch_name: str,
    ) -> Path:

        paths = BatchPaths(
            batch_name,
        )

        # Create required folder structure
        paths.create()

        print(
            f"Batch Folder : {paths.batch_folder}"
        )

        return paths.temp