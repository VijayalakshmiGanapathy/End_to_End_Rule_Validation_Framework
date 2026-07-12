import logging

from app.core.paths import BatchPaths

from app.core.config import (
    RUN_MODE_SINGLE_T2,
    RUN_MODE_ALL_T2,
    RUN_MODE_T2,
    SINGLE_BATCH_T2,
)

from app.selenium.selenium_driver import SeleniumDriver
from app.services.injection_harness_service import (
    InjectionHarnessService,
)


from app.services.p21_service import P21Service

from app.services.validation_service import ValidationService

from app.services.test_approach2.batch_config_service_t2 import (
    BatchConfigService,
)

from app.services.kwalify_service import KwalifyService

logger = logging.getLogger(__name__)


class AutomationService:
    """
    Executes the complete automation workflow for one batch.

    Workflow
    --------
    
    
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

            logger.info(
                "=" * 80
            )

            logger.info(
                "Test Approach 2"
            )

            logger.info(
                "Using Manual Original Data"
            )

            logger.info(
                f"Original Data Folder : {paths.original_data}"
            )

            logger.info(
                "=" * 80
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
        logger.info("Starting Test Approach 2 - All Batches")
        logger.info("=" * 80)

        batch_service = BatchConfigService()

        if RUN_MODE_T2.lower() == RUN_MODE_SINGLE_T2:

            logger.info(
                f"Run Mode : SINGLE ({SINGLE_BATCH_T2})"
            )

            batch_configs = [
                batch_service.get_batch_configuration(
                    SINGLE_BATCH_T2,
                )
            ]

        elif RUN_MODE_T2.lower() == RUN_MODE_ALL_T2:

            logger.info(
                "Run Mode : ALL"
            )

            batch_configs = (
                batch_service.get_all_batches()
            )

        else:

            raise ValueError(
                "RUN_MODE_T2 must be 'single' or 'all'."
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
        logger.info("Test Approach 2 Completed")
        logger.info(f"Total     : {total}")
        logger.info(f"Completed : {completed}")
        logger.info(f"Failed    : {failed}")
        logger.info("=" * 80)