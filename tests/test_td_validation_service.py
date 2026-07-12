"""
Test TD Validation Service
"""
import logging

#from app.core.logging_config import logger
from app.services.td_report_service import TDReportService
from app.services.td_validation_service import TDValidationService




logger = logging.getLogger(__name__)


def test_td_validation_service():
    """
    Test TD Validation Service.
    """

    logger.info("=" * 80)
    logger.info("TD Validation Test Started")
    logger.info("=" * 80)

    batch = "B01_DM_dates"

    try:

        # -------------------------------------------------------------
        # Validate
        # -------------------------------------------------------------

        validation_service = TDValidationService()

        report_df = validation_service.validate(
            batch=batch,
        )

        assert report_df is not None

        assert not report_df.empty

        logger.info(
            "Validation completed successfully."
        )

        # -------------------------------------------------------------
        # Generate Report
        # -------------------------------------------------------------

        report_service = TDReportService()

        report_file = report_service.generate_report(
            batch=batch,
            report_df=report_df,
        )

        assert report_file.exists()

        logger.info(
            "Report generated successfully : %s",
            report_file,
        )

        logger.info("=" * 80)
        logger.info("TD Validation Test Completed")
        logger.info("=" * 80)

    except Exception:

        logger.exception(
            "TD Validation Test Failed."
        )

        raise