from pathlib import Path
from app.services.archive_service import ArchiveService
from pathlib import Path

import logging
import shutil
import time

logger = logging.getLogger(__name__)


class TrialGenDownloadService:
    """
    Handles TrialGen dataset download operations.

    Responsibilities:
        1. Wait for TrialGen ZIP download.
        2. Rename downloaded ZIP.
        3. Return renamed ZIP path.
    """

    @staticmethod
    def wait_for_download(
        temp_folder: Path,
        batch_name: str,
        timeout: int = 180,
    ) -> Path:
        """
        Wait for the TrialGen dataset ZIP to finish downloading.

        Args:
            temp_folder:
                Temporary download folder.

            batch_name:
                Current batch name.

            timeout:
                Maximum wait time in seconds.

        Returns:
            Path to the downloaded ZIP file.

        Raises:
            TimeoutError:
                If the download is not completed within
                the specified timeout.
        """

        try:

            logger.info(
                f"Batch: {batch_name} | Download | Waiting for TrialGen ZIP download."
            )

            start_time = time.time()

            while time.time() - start_time < timeout:

                zip_files = list(
                    temp_folder.glob("dataset_*.zip")
                )

                if zip_files:

                    zip_file = zip_files[0]

                    logger.info(
                        f"Batch: {batch_name} | Download | Download completed: {zip_file.name}"
                    )

                    return zip_file

                time.sleep(1)

            logger.error(
                f"Batch: {batch_name} | Download | Download timed out."
            )

            raise TimeoutError(
                "TrialGen ZIP download timed out."
            )

        except Exception:

            logger.exception(
                f"Batch: {batch_name} | Download | Failed while waiting for download."
            )

            raise

    @staticmethod
    def rename_download(
        zip_file: Path,
        batch_name: str,
    ) -> Path:
        """
        Rename the downloaded TrialGen ZIP file.

        Example:
            dataset_xxxxx.zip

            →

            trialgen_B01_DM_dates_zip.zip

        Args:
            zip_file:
                Downloaded ZIP file.

            batch_name:
                Current batch name.

        Returns:
            Path to the renamed ZIP file.
        """

        try:

            logger.info(
                f"Batch: {batch_name} | Download | Renaming downloaded ZIP."
            )

            renamed_file = zip_file.parent / (
                f"trialgen_{batch_name}_zip.zip"
            )

            if renamed_file.exists():

                logger.warning(
                    f"Batch: {batch_name} | Download | Existing ZIP found. Deleting old file."
                )

                renamed_file.unlink()

            shutil.move(
                zip_file,
                renamed_file,
            )

            logger.info(
                f"Batch: {batch_name} | Download | ZIP renamed to: {renamed_file.name}"
            )

            return renamed_file

        except Exception:

            logger.exception(
                f"Batch: {batch_name} | Download | Failed to rename ZIP file."
            )

            raise

    def process_download(
        self,
        temp_folder,
        original_data_folder,
        batch_name,
    ):
        """
        Process TrialGen download.
        """

        zip_file = self.wait_for_download(
            temp_folder,
            batch_name,
        )

        zip_file = self.rename_download(
            zip_file,
            batch_name,
        )

        ArchiveService.extract_archive(
            zip_file,
            original_data_folder,
        )

        ArchiveService.verify_trialgen_extraction(
            original_data_folder,
        )

        ArchiveService.delete_archive(
            zip_file,
        )

    

    def clear_download_folder(self, download_folder):

        download_folder = Path(download_folder)

        # Create the folder if it doesn't exist
        download_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(f"Clearing download folder: {download_folder}")

        for file in download_folder.iterdir():

            if file.is_file():
                file.unlink()

            elif file.is_dir():
                import shutil
                shutil.rmtree(file)