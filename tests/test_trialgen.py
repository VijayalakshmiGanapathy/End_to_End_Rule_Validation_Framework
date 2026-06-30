import logging

from app.core.paths import BatchPaths
from app.selenium.download_manager import DownloadManager
from app.selenium.selenium_driver import SeleniumDriver
from app.services.archive_service import ArchiveService
from app.services.batch_config_service import BatchConfigService
from app.services.trialgen_download_service import (
    TrialGenDownloadService,
)
from app.services.trialgen_service import TrialGenService

logger = logging.getLogger(__name__)


def test_trialgen():
    """
    Execute the complete TrialGen workflow for a batch.

    Workflow
    --------
    1. Read batch configuration.
    2. Create batch folder structure.
    3. Generate TrialGen dataset.
    4. Download TrialGen ZIP.
    5. Rename downloaded ZIP.
    6. Extract ZIP into Original_data.
    7. Verify extraction.
    8. Delete ZIP archive.
    """

    driver = None

    try:

        # -----------------------------------------
        # Load batch configuration
        # -----------------------------------------

        config = BatchConfigService().get_batch_configuration(
            "B01_DM_dates",
        )

        logger.info(
            f"Batch: {config.batch_name} | Test | TrialGen workflow started."
        )

        # -----------------------------------------
        # Create Batch Folder Structure
        # -----------------------------------------

        paths = BatchPaths(
            config.batch_name,
        )

        paths.create()

        # -----------------------------------------
        # Download Folder
        # -----------------------------------------

        folder = DownloadManager.get_batch_download_folder(
            config.batch_name,
        )

        logger.info(
            f"Batch: {config.batch_name} | Test | Download folder: {folder}"
        )

        # -----------------------------------------
        # Selenium
        # -----------------------------------------

        driver = SeleniumDriver(
            folder,
        ).get_driver()

        trialgen = TrialGenService(
            driver,
            config.batch_name,
        )

        # -----------------------------------------
        # Execute TrialGen
        # -----------------------------------------

        trialgen.run(
            config.host_generator_key,
        )

        # -----------------------------------------
        # Download ZIP
        # -----------------------------------------

        download_service = TrialGenDownloadService()

        zip_file = download_service.wait_for_download(
            folder,
            config.batch_name,
        )

        zip_file = download_service.rename_download(
            zip_file,
            config.batch_name,
        )

        # -----------------------------------------
        # Extract ZIP
        # -----------------------------------------

        ArchiveService.extract_archive(
            zip_file,
            paths.original_data,
        )

        ArchiveService.verify_trialgen_extraction(
            paths.original_data,
        )

        ArchiveService.delete_archive(
            zip_file,
        )

        logger.info(
            f"Batch: {config.batch_name} | Test | TrialGen workflow completed successfully."
        )

    except Exception:

        logger.exception(
            "TrialGen workflow execution failed."
        )

        raise

    finally:

        if driver:

            driver.quit()

            logger.info(
                "Selenium browser closed."
            )


if __name__ == "__main__":

    test_trialgen()