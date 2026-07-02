from pathlib import Path
import logging
import shutil
import time

from app.services.archive_service import ArchiveService

from app.core.config import (
    MANIFEST_FILE,
    DIRTY_ZIP_FILE,
    EXPORT_SUMMARY_FILE,
    EXPORT_AUDIT_REPORT_FILE,
    JSON_EXTENSION,
    ZIP_EXTENSION,
    EXCEL_EXTENSION,

)
from app.core.constants import DIRTY_FOLDER,CSV_EXTENSION 
from app.core.paths import BatchPaths


logger = logging.getLogger(__name__)


class InjectionDownloadService:
    """
    Handles download, rename and extraction of
    Injection Harness output files.
    """

    @staticmethod
    def wait_for_download(
        folder: Path,
        pattern: str,
        timeout: int = 300,
    ) -> Path:
        """
        Wait until a new downloaded file appears.

        Parameters
        ----------
        folder : Path
            Download folder.

        pattern : str
            File search pattern.

        timeout : int
            Maximum wait time.

        Returns
        -------
        Path
            Downloaded file path.
        """

        logger.info(
            f"Waiting for download: {pattern}"
        )
        print("\nFiles currently in temp folder:")
        for file in folder.iterdir():
            print(file.name)

        # Files already present before download starts
        existing_files = {
            file.name
            for file in folder.glob(pattern)
        }

        start_time = time.time()

        while time.time() - start_time < timeout:

            for file in folder.glob(pattern):

                # Ignore partially downloaded files
                if file.name.endswith(".crdownload"):
                    continue

                # Ignore files that already existed
                if file.name in existing_files:
                    continue

                logger.info(
                    f"Downloaded: {file.name}"
                )

                return file

            time.sleep(1)

        raise TimeoutError(
            f"Download timeout: {pattern}"
        )

    @staticmethod
    def rename_file(
        source: Path,
        destination: Path,
    ) -> Path:
        """
        Rename downloaded file.
        """

        # If the file already has the correct name,
        # don't rename it.
        if source.resolve() == destination.resolve():

            logger.info(
                f"File already named: {source.name}"
            )

            return source

        if destination.exists():

            logger.info(
                f"Deleting existing file: {destination.name}"
            )

            destination.unlink()

        shutil.move(
            source,
            destination,
        )

        logger.info(
            f"Renamed -> {destination.name}"
        )

        return destination
    
    @staticmethod
    def process_manifest(
        temp_folder: Path,
        batch_folder: Path,
        paths,
    ) -> Path:
        """
        Wait and rename manifest.json.
        """

        manifest = InjectionDownloadService.wait_for_download(
            temp_folder,
            "manifest*.json",
        )

        destination = (
            batch_folder /
            f"{MANIFEST_FILE}_{paths.batch_prefix}{JSON_EXTENSION}"
        )

        return InjectionDownloadService.rename_file(
            manifest,
            destination,
        )

    @staticmethod
    def process_dirty_csv(
        temp_folder: Path,
        batch_folder: Path,
        batch_name: str,
    ):
        """
        Wait, rename, extract and delete
        dirty CSV archive.
        """

        archive = InjectionDownloadService.wait_for_download(
            temp_folder,
            "*.zip",
        )

        renamed_archive = (
            temp_folder /
            f"{DIRTY_ZIP_FILE}_{batch_name}{ZIP_EXTENSION}"
        )

        archive = InjectionDownloadService.rename_file(
            archive,
            renamed_archive,
        )

        logger.info(
            f"ZIP File : {archive}"
        )

        if not archive.exists():

            raise FileNotFoundError(
                f"{archive} does not exist."
            )
        
        from app.core.paths import BatchPaths

        paths = BatchPaths(batch_name)

        ArchiveService.extract_archive(
            archive,
            paths.batch_folder,
            clean_folder=DIRTY_FOLDER,
        )

        ArchiveService.verify_dirty_extraction(
            paths.dirty,
        )

        ArchiveService.delete_archive(
            archive,
        )

        logger.info(
            "Dirty CSV extraction completed."
        )

    @staticmethod
    def process_excel_download(
        temp_folder: Path,
        batch_folder: Path,
        batch_name: str,
        output_name: str,
    ) -> Path:
        """
        Wait, rename and move an Excel download.
        """

        excel_file = InjectionDownloadService.wait_for_download(
            temp_folder,
            "*.xlsx",
        )

        destination = (
            batch_folder /
            f"{output_name}_{batch_name}.xlsx"
        )

        return InjectionDownloadService.rename_file(
            excel_file,
            destination,
        )

    @staticmethod
    def process_export_summary(
        temp_folder: Path,
        batch_folder: Path,
        paths,
    ) -> Path:
        """
        Wait for Export Summary CSV,
        rename it and move it to the batch folder.
        """

        # Wait for downloaded CSV
        summary = InjectionDownloadService.wait_for_download(
            temp_folder,
            "*_export.csv",
        )

        
        destination = (
            batch_folder /
            f"{EXPORT_SUMMARY_FILE}_{paths.batch_prefix}.csv"
        )

        # Delete old file if it exists
        if destination.exists():

            logger.info(
                f"Deleting existing file: {destination.name}"
            )

            destination.unlink()

        # Move + Rename
        shutil.move(
            summary,
            destination,
        )

        logger.info(
            f"Export Summary saved as {destination.name}"
        )

        return destination

    @staticmethod
    def process_audit_report(
        temp_folder: Path,
        batch_folder: Path,
        paths,
    ) -> Path:
        """
        Wait, rename and move Audit Report.
        """

        audit = InjectionDownloadService.wait_for_download(
            temp_folder,
            "*_export.csv",
        )

    

        destination = (
            batch_folder /
            f"{EXPORT_AUDIT_REPORT_FILE}_{paths.batch_prefix}.csv"
        )

        return InjectionDownloadService.rename_file(
            audit,
            destination,
        )