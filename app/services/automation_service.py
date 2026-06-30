import logging

from app.core.paths import BatchPaths
from app.selenium.selenium_driver import SeleniumDriver
from app.services.injection_harness_service import (
    InjectionHarnessService,
)
from app.services.trialgen_download_service import (
    TrialGenDownloadService,
)
from app.services.trialgen_service import TrialGenService

logger = logging.getLogger(__name__)


class AutomationService:
    """
    Executes the complete automation workflow for one batch.

    Workflow
    --------
    1. Generate Original Data using TrialGen.
    2. Download TrialGen ZIP.
    3. Extract ZIP into Original_data.
    4. Open SDTM Error Injection Harness.
    5. Upload Original_data.
    6. Inject all rules.
    7. Download:
        - manifest.json
        - dirty CSV
        - export summary
        - audit report
    """

    def run_batch(
        self,
        config,
    ):

        driver = None

        try:

            logger.info(
                "=" * 80
            )

            logger.info(
                f"Starting Batch : {config.batch_name}"
            )

            logger.info(
                "=" * 80
            )

            # -----------------------------------------
            # Prepare Folder Structure
            # -----------------------------------------

            paths = BatchPaths(
                config.batch_name,
            )

            logger.info(
                f"Batch Folder : {paths.batch_folder}"
            )

            # -----------------------------------------
            # Start Selenium
            # -----------------------------------------

            driver = SeleniumDriver(
                paths.temp,
            ).get_driver()

            # -----------------------------------------
            # TrialGen
            # -----------------------------------------

            logger.info(
                "Starting TrialGen..."
            )

            trialgen = TrialGenService(
                driver,
                config.batch_name,
            )

            trialgen.run(
                config.host_generator_key,
            )

            TrialGenDownloadService().process_download(
                paths.temp,
                paths.original_data,
                config.batch_name,
            )

            logger.info(
                "TrialGen completed successfully."
            )

            # -----------------------------------------
            # SDTM Error Injection Harness
            # -----------------------------------------

            logger.info(
                "Starting Injection Harness..."
            )

            injection = InjectionHarnessService(
                driver,
                config.batch_name,
            )

            injection.run(
                paths.original_data,
                config.rule_ids,
                paths.temp,
                paths.batch_folder,
            )

            logger.info(
                "Injection Harness completed successfully."
            )

            logger.info(
                f"{config.batch_name} completed successfully."
            )

        except Exception:

            logger.exception(
                f"{config.batch_name} failed."
            )

            raise

        finally:

            if driver:

                driver.quit()

                logger.info(
                    "Browser closed."
                )