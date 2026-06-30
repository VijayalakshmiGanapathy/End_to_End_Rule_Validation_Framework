import logging

from app.core.paths import BatchPaths
from app.selenium.download_manager import DownloadManager
from app.selenium.selenium_driver import SeleniumDriver
from app.services.batch_config_service import BatchConfigService
from app.services.injection_harness_service import (
    InjectionHarnessService,
)

logger = logging.getLogger(__name__)


def test_injection_harness():
    """
    Execute the SDTM Error Injection Harness workflow.

    Workflow
    --------
    1. Load batch configuration.
    2. Create batch folder structure.
    3. Launch Selenium.
    4. Upload Original_data.
    5. Select Rules.
    6. Run Injection.
    7. Download Results.
    """

    driver = None

    try:

        # -------------------------------------------------
        # Load batch configuration
        # -------------------------------------------------

        config = BatchConfigService().get_batch_configuration(
            "B01_DM_dates",
        )

        logger.info(
            f"Batch: {config.batch_name} | Test | Injection Harness workflow started."
        )

        # -------------------------------------------------
        # Batch Paths
        # -------------------------------------------------

        paths = BatchPaths(
            config.batch_name,
        )

        paths.create()

        logger.info(
            f"Batch: {config.batch_name} | Test | Batch Folder: {paths.batch_folder}"
        )

        logger.info(
            f"Batch: {config.batch_name} | Test | Original Data Folder: {paths.original_data}"
        )

        logger.info(
            f"Batch: {config.batch_name} | Test | Temp Folder: {paths.temp}"
        )

        # -------------------------------------------------
        # Download Folder
        # -------------------------------------------------

        download_folder = DownloadManager.get_batch_download_folder(
            config.batch_name,
        )

        # -------------------------------------------------
        # Selenium
        # -------------------------------------------------

        driver = SeleniumDriver(
            download_folder,
        ).get_driver()

        injection = InjectionHarnessService(
            driver,
            config.batch_name,
        )

        # -------------------------------------------------
        # Execute Injection Harness Workflow
        # -------------------------------------------------

        injection.run(
            paths.original_data,
            config.rule_ids,
            paths.temp,
            paths.batch_folder,
        )

        logger.info(
            f"Batch: {config.batch_name} | Test | Injection Harness workflow completed successfully."
        )

    except Exception:

        logger.exception(
            "Injection Harness workflow failed."
        )

        raise

    finally:

        if driver:

            driver.quit()

            logger.info(
                "Selenium browser closed."
            )


if __name__ == "__main__":

    test_injection_harness()