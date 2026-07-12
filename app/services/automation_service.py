import logging

from app.core.paths import BatchPaths

from app.core.config import (
    RUN_MODE_SINGLE,
    RUN_MODE_ALL,
    RUN_MODE,
    SINGLE_BATCH,
)

from app.selenium.selenium_driver import SeleniumDriver
from app.services.injection_harness_service import (
    InjectionHarnessService,
)
from app.services.trialgen_download_service import (
    TrialGenDownloadService,
)
from app.services.trialgen_service import TrialGenService

from app.services.p21_service import P21Service

from app.services.validation_service import ValidationService

from app.services.batch_config_service import BatchConfigService

from app.services.kwalify_service import KwalifyService

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

            TrialGenDownloadService().clear_download_folder(
                paths.temp,
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
                paths,
            )

            logger.info(
                "Injection Harness completed successfully."
            )

            logger.info(
                f"{config.batch_name} completed successfully."
            )

            

            p21 = P21Service()

            report_file, run_number = p21.get_next_report_file(
                paths,
            )

            logger.info(
                f"P21 Report : {report_file.name}"
            )

            logger.info(
                f"P21 Run Number : {run_number}"
            )

            result = p21.run(
                paths.dirty,
                report_file,
            )

            if not result["success"]:
                raise Exception("P21 validation failed.")

            logger.info(
                "P21 validation completed successfully."
            )

            
        
            validation = ValidationService()

            validation.run(
                paths,
                config,
                report_file,
            )

            logger.info(
                "Validation completed successfully."
            )

            # logger.info(
            #     "Starting Kwalify Validation..."
            # )

            # KwalifyService().run(
            #     paths,
            #     config,
            #     run_number,
            # )

            # logger.info(
            #     "Kwalify Validation Completed."
            # )
            # return run_number
    
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


    def run_all_batches(self):

        logger.info("=" * 80)
        logger.info("Starting Test Approach 1 - All Batches")
        logger.info("=" * 80)

        batch_service = BatchConfigService()

        if RUN_MODE.lower() == RUN_MODE_SINGLE:

            logger.info(
                f"Run Mode : SINGLE ({SINGLE_BATCH})"
            )

            batch_configs = [
                batch_service.get_batch_configuration(
                    SINGLE_BATCH,
                )
            ]

        elif RUN_MODE.lower() == RUN_MODE_ALL:

            logger.info(
                "Run Mode : ALL"
            )

            batch_configs = (
                batch_service.get_all_batches()
            )

        else:

            raise ValueError(
                "RUN_MODE must be 'single' or 'all'."
            )
        
        total = len(batch_configs)
        completed = 0
        failed = 0

        logger.info(f"Total Batches : {total}")

        for config in batch_configs:

            try:

                self.run_batch(config)

                completed += 1

            except Exception:

                failed += 1

                logger.exception(
                    f"{config.batch_name} failed."
                )

                # Continue with the next batch
                continue

        logger.info("=" * 80)
        logger.info("Test Approach 1 Completed")
        logger.info(f"Total     : {total}")
        logger.info(f"Completed : {completed}")
        logger.info(f"Failed    : {failed}")
        logger.info("=" * 80)