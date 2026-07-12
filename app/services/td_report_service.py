"""
TD Report Service

Generates the TD Validation Excel report.

Sheets:
    1. Validation_Report
    2. Summary
"""

from pathlib import Path

import pandas as pd

#from app.core.logging_config import logger
from app.core.paths import BatchPaths

import logging

from app.core.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

class TDReportService:
    """
    Generate TD Validation Report.
    """

    def generate_report(
        self,
        batch: str,
        report_df: pd.DataFrame,
    ) -> Path:
        """
        Generate TD Validation Report.

        Parameters
        ----------
        batch : str
            Batch Name.

        report_df : DataFrame
            Validation report.

        Returns
        -------
        Path
            Generated report path.
        """

        logger.info("=" * 80)
        logger.info("Generating TD Validation Report")
        logger.info("=" * 80)

        try:

            paths = BatchPaths(batch)

            # ----------------------------------------------------------
            # Add Serial Number
            # ----------------------------------------------------------

            report_df.insert(
                0,
                "S.No",
                range(1, len(report_df) + 1),
            )

            # ----------------------------------------------------------
            # Build Summary
            # ----------------------------------------------------------

            summary_df = self._build_summary(
                report_df,
            )

            # ----------------------------------------------------------
            # Output File
            # ----------------------------------------------------------

            output_file = paths.td_validation_report

            logger.info(
                "Output Report : %s",
                output_file,
            )

            # ----------------------------------------------------------
            # Write Report
            # ----------------------------------------------------------

            self._write_report(
                sheets={
                    "Validation_Report": report_df,
                    "Summary": summary_df,
                },
                output_file=output_file,
            )

            logger.info(
                "TD Validation Report Generated Successfully."
            )

            return output_file

        except Exception:

            logger.exception(
                "Failed to generate TD Validation Report."
            )

            raise

    # ==============================================================
    # Summary
    # ==============================================================

    def _build_summary(
        self,
        report_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build Summary sheet.
        """

        logger.info(
            "Preparing Summary Sheet."
        )

        summary = [

            [
                "Total Working Rules",
                len(report_df),
            ],

            [
                "Target Rules",
                len(report_df),
            ],

            [
                "Skipped Rules",
                (
                    report_df["Skipped Rule"]
                    == "YES"
                ).sum(),
            ],

            [
                "Rule Missing in P21",
                (
                    report_df["P21 Issue Summary Present"]
                    == "NO"
                ).sum(),
            ],

            [
                "PASS",
                (
                    report_df["Final Status"]
                    == "PASS"
                ).sum(),
            ],

            [
                "FAIL",
                (
                    report_df["Final Status"]
                    == "FAIL"
                ).sum(),
            ],
        ]

        return pd.DataFrame(
            summary,
            columns=[
                "Metric",
                "Count",
            ],
        )

    # ==============================================================
    # Write Excel Report
    # ==============================================================

    def _write_report(
        self,
        sheets: dict[str, pd.DataFrame],
        output_file: Path,
    ) -> None:
        """
        Write all DataFrames to Excel.

        Parameters
        ----------
        sheets : dict
            Dictionary of sheet name and DataFrame.

        output_file : Path
            Output excel file.
        """

        logger.info(
            "Writing Excel Report."
        )

        with pd.ExcelWriter(
            output_file,
            engine="openpyxl",
        ) as writer:

            for sheet_name, dataframe in sheets.items():

                dataframe.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                )

        logger.info(
            "Excel Report Saved Successfully."
        )