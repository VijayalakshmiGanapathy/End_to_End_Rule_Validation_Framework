import logging

from app.core.paths import BatchPaths
from app.services.batch_config_service import BatchConfigService
from app.services.p21_service import P21Service
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


def test_validation_service():

    # -----------------------------------------
    # Batch Configuration
    # -----------------------------------------

    config = BatchConfigService().get_batch_configuration(
        "B16_Destructive_DropDomain",
    )

    # -----------------------------------------
    # Batch Paths
    # -----------------------------------------

    paths = BatchPaths(
        config.batch_name,
    )

    # -----------------------------------------
    # Find Latest P21 Report
    # -----------------------------------------

    p21 = P21Service()

    report_files = sorted(
        paths.p21_reports.glob("*.xlsx")
    )

    if not report_files:

        raise FileNotFoundError(
            "No P21 report found."
        )

    report_file = report_files[-1]

    logger.info(
        f"Using P21 Report : {report_file.name}"
    )

    # -----------------------------------------
    # Execute Validation
    # -----------------------------------------

    validation = ValidationService()

    validation.run(
        paths,
        config,
        report_file,
    )

    logger.info(
        "Validation completed successfully."
    )


if __name__ == "__main__":

    test_validation_service()