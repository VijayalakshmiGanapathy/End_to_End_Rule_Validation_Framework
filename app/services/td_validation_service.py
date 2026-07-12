"""
TD Validation Service

This service validates each Rule ID from the Working Rules file against

1. P21 Issue Summary
2. P21 Rules
3. SDTMIG Study
4. SDTMIG Test Case
5. SDTMIG Rule Cases

The service returns a pandas DataFrame which will later be used
by TDReportService to generate the Excel report.
"""

from pathlib import Path

import pandas as pd

from app.core.paths import BatchPaths

from app.core.config import (
    WORKING_RULES_FILE,
    TEST_CASE_FILE,
    WORKING_RULES_SHEET,
    ISSUE_SUMMARY_SHEET,
    P21_RULES_SHEET,
    STUDY_SHEET,
    RULE_SHEET,
    TEST_CASE_SHEET
)



import logging

from app.core.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)




from app.utils.file_reader import (
    read_excel_sheet,
    clean_columns,
)



class TDValidationService:
    """
    Performs validation between

    - Working Rules
    - SDTMIG
    - P21 Report

    Returns
    -------
    pandas.DataFrame
        Validation report.
    """

    def validate(
        self,
        batch: str | None = None,
        host_generator_key: str | None = None,
    ) -> pd.DataFrame:
        """
        Perform Rule ID validation.

        Parameters
        ----------
        batch : str, optional
            Batch name.

        host_generator_key : str, optional
            TrialGen Host Generator Key.

        Returns
        -------
        pandas.DataFrame
        """

        logger.info("=" * 80)
        logger.info("TD Validation Started")
        logger.info("=" * 80)

        try:

            # ------------------------------------------------------------------
            # Load Working Rules
            # ------------------------------------------------------------------

            working_df = self._load_working_rules(
                batch=batch,
                host_generator_key=host_generator_key,
            )

            logger.info(
                "Total Working Rules : %s",
                len(working_df),
            )

            # ------------------------------------------------------------------
            # Load SDTMIG Master
            # ------------------------------------------------------------------

            (
                study_df,
                test_case_df,
                rule_cases_df,
            ) = self._load_sdtmig()

            logger.info("SDTMIG Master Loaded Successfully")

            results = []

            # ------------------------------------------------------------------
            # Validate every Rule
            # ------------------------------------------------------------------

            for _, row in working_df.iterrows():

                logger.info(
                    "Validating Rule ID : %s",
                    row["Rule ID"],
                )

                result = self._validate_rule(
                    row=row,
                    study_df=study_df,
                    test_case_df=test_case_df,
                    rule_cases_df=rule_cases_df,
                )

                results.append(result)

            report_df = pd.DataFrame(results)

            logger.info(
                "Validation Completed Successfully."
            )

            logger.info(
                "Total Records Generated : %s",
                len(report_df),
            )

            return report_df

        except Exception as ex:

            logger.exception(
                "Error while validating Rule IDs."
            )

            raise RuntimeError(
                "TD Validation Failed."
            ) from ex

    # ==================================================================
    # Load Working Rules
    # ==================================================================

    def _load_working_rules(
        self,
        batch: str |None,
        host_generator_key: str |None,
    ) -> pd.DataFrame:
        """
        Load Working Rules file.
        """

        logger.info(
            "Loading Working Rules..."
        )

        df = clean_columns(
            read_excel_sheet(
                WORKING_RULES_FILE,
                WORKING_RULES_SHEET,
            )
        )

        required_columns = [
            "Batch",
            "Host Generator Key",
            "Rule ID",
            "Domain",
            "Total Findings",
        ]

        self._check_required_columns(
            df,
            required_columns,
            WORKING_RULES_SHEET,
        )

        if batch:

            logger.info(
                "Filtering Batch : %s",
                batch,
            )

            df = df[
                df["Batch"]
                .astype(str)
                .str.strip()
                == batch
            ]

        if host_generator_key:

            logger.info(
                "Filtering Host Generator Key : %s",
                host_generator_key,
            )

            df = df[
                df["Host Generator Key"]
                .astype(str)
                .str.strip()
                == host_generator_key
            ]

        logger.info(
            "Working Rules Loaded : %s",
            len(df),
        )

        return df

    # ==================================================================
    # Load SDTMIG
    # ==================================================================

    def _load_sdtmig(
        self,
    ) -> tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
    ]:
        """
        Load SDTMIG sheets.
        """

        logger.info(
            "Loading SDTMIG Workbook..."
        )

        study_df = clean_columns(
            read_excel_sheet(
                TEST_CASE_FILE,
                STUDY_SHEET,
            )
        )

        test_case_df = clean_columns(
            read_excel_sheet(
                TEST_CASE_FILE,
                TEST_CASE_SHEET,
            )
        )

        rule_cases_df = clean_columns(
            read_excel_sheet(
                TEST_CASE_FILE,
                RULE_SHEET,
            )
        )

        logger.info(
            "SDTMIG Workbook Loaded Successfully."
        )

        return (
            study_df,
            test_case_df,
            rule_cases_df,
        )

    # ==================================================================
    # Find P21 Report
    # ==================================================================

  

    def _find_p21_report(
        self,
        batch: str,
    ) -> Path:
        """
        Find the P21 report for the given batch.

        Example:
            data/batches/B01_DM_dates/P21_reports/P21_B01_Run1.xlsx
        """

        logger.info(
            "Searching P21 Report for Batch : %s",
            batch,
        )

        paths = BatchPaths(batch)

        reports = sorted(
            paths.p21_reports.glob("P21_*.xlsx")
        )

        if not reports:

            logger.error(
                "No P21 report found in %s",
                paths.p21_reports,
            )

            raise FileNotFoundError(
                f"No P21 report found in {paths.p21_reports}"
            )

        p21_report = reports[0]

        logger.info(
            "P21 Report Found : %s",
            p21_report.name,
        )

        return p21_report

    # ==================================================================
    # Load P21 Report
    # ==================================================================

    def _load_p21_report(
        self,
        report_file: Path,
    ) -> tuple[
        pd.DataFrame,
        pd.DataFrame,
    ]:
        """
        Load Issue Summary and Rules sheet.
        """

        logger.info(
            "Loading P21 Report : %s",
            report_file.name,
        )

        issue_df = clean_columns(
            read_excel_sheet(
                report_file,
                ISSUE_SUMMARY_SHEET,
                
            )
        )

        issue_df["Source"] = (
            issue_df["Source"]
            .ffill()
            .astype(str)
            .str.strip()
        )

        rules_df = clean_columns(
            read_excel_sheet(
                report_file,
                P21_RULES_SHEET,
            )
        )

        
        logger.info(
            "P21 Report Loaded Successfully."
        )

        return (
            issue_df,
            rules_df,
        )
    
    # ==================================================================
    # Validate Rule
    # ==================================================================

    def _validate_rule(
        self,
        row: pd.Series,
        study_df: pd.DataFrame,
        test_case_df: pd.DataFrame,
        rule_cases_df: pd.DataFrame,
    ) -> dict:
        """
        Validate a single Rule ID against:
            - P21 Issue Summary
            - P21 Rules
            - SDTMIG Study
            - SDTMIG Test Case
            - SDTMIG Rule Cases

        Returns
        -------
        dict
            Validation result for one rule.
        """

        try:

            batch = str(row["Batch"]).strip()
            host_generator_key = str(row["Host Generator Key"]).strip()
            rule_id = str(row["Rule ID"]).strip()
            expected_domain = str(row["Domain"]).strip()

            logger.info(
                "Processing Rule ID [%s] for Batch [%s]",
                rule_id,
                batch,
            )

            # ----------------------------------------------------------
            # Find corresponding P21 report
            # ----------------------------------------------------------

            p21_report = self._find_p21_report(batch)

            if p21_report is None:

                logger.warning(
                    "P21 Report not found for Batch [%s]",
                    batch,
                )

                return {
                    "Batch": batch,
                    "Host Generator Key": host_generator_key,
                    "Rule ID": rule_id,
                    "Expected Domain": expected_domain,
                    "P21 Domain": "",
                    "Domain Match": "NO",
                    "P21 Issue Summary Present": "NO",
                    "P21 Rules Present": "NO",
                    "SDTMIG Study Present": "NO",
                    "SDTMIG Test Case Present": "NO",
                    "SDTMIG Rule Cases Present": "NO",
                    "Skipped Rule": "NO",
                    "Final Status": "FAIL",
                    "Remarks": "P21 Report not found",
                }

            # ----------------------------------------------------------
            # Load P21 Report
            # ----------------------------------------------------------

            issue_df, rules_df = self._load_p21_report(
                p21_report
            )

            # ----------------------------------------------------------
            # Issue Summary Validation
            # ----------------------------------------------------------

            issue_matches = issue_df[
                issue_df["Pinnacle 21 ID"]
                .astype(str)
                .str.strip()
                == rule_id
            ]

            issue_present = not issue_matches.empty

            p21_domain = ""

            if issue_present:

                p21_domain = ", ".join(
                    sorted(
                        issue_matches["Source"]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .unique()
                    )
                )

            # ----------------------------------------------------------
            # Domain Validation
            # ----------------------------------------------------------

            domain_match = False

            if issue_present:

                domain_match = (
                    expected_domain
                    in p21_domain.split(", ")
                )

            # ----------------------------------------------------------
            # P21 Rules Validation
            # ----------------------------------------------------------

            p21_rules_present = (
                rules_df["Pinnacle 21 ID"]
                .astype(str)
                .str.strip()
                == rule_id
            ).any()

            # ----------------------------------------------------------
            # SDTMIG Study Validation
            # ----------------------------------------------------------

            study_present = (
                study_df["Rule ID"]
                .astype(str)
                .str.strip()
                == rule_id
            ).any()

            # ----------------------------------------------------------
            # SDTMIG Test Case Validation
            # ----------------------------------------------------------

            test_case_present = (
                test_case_df["Rule ID"]
                .astype(str)
                .str.strip()
                == rule_id
            ).any()

            # ----------------------------------------------------------
            # SDTMIG Rule Cases Validation
            # ----------------------------------------------------------

            rule_cases_present = self._check_rule_cases(
                rule_cases_df,
                rule_id,
            )

            # ----------------------------------------------------------
            # Skipped Rule
            # ----------------------------------------------------------

            skipped_rule = self._is_skipped_rule(row)

            # ----------------------------------------------------------
            # Final Status
            # ----------------------------------------------------------

            checks = [

                issue_present,

                p21_rules_present,

                study_present,

                test_case_present,

                rule_cases_present,

                domain_match,

                not skipped_rule,

            ]

            final_status = (
                "PASS"
                if all(checks)
                else "FAIL"
            )

            # ----------------------------------------------------------
            # Remarks
            # ----------------------------------------------------------

            remarks = self._build_remarks(
                issue_present=issue_present,
                p21_rule_present=p21_rules_present,
                study_present=study_present,
                test_case_present=test_case_present,
                rule_cases_present=rule_cases_present,
                domain_match=domain_match,
                skipped_rule=skipped_rule,
            )

            logger.info(
                "Rule [%s] Validation Completed : %s",
                rule_id,
                final_status,
            )

            return {

                "Batch": batch,

                "Host Generator Key": host_generator_key,

                "Rule ID": rule_id,

                "Expected Domain": expected_domain,

                "P21 Domain": p21_domain,

                "Domain Match":
                    "YES"
                    if domain_match
                    else "NO",

                "P21 Issue Summary Present":
                    "YES"
                    if issue_present
                    else "NO",

                "P21 Rules Present":
                    "YES"
                    if p21_rules_present
                    else "NO",

                "SDTMIG Study Present":
                    "YES"
                    if study_present
                    else "NO",

                "SDTMIG Test Case Present":
                    "YES"
                    if test_case_present
                    else "NO",

                "SDTMIG Rule Cases Present":
                    "YES"
                    if rule_cases_present
                    else "NO",

                "Skipped Rule":
                    "YES"
                    if skipped_rule
                    else "NO",

                "Final Status": final_status,

                "Remarks": remarks,
            }

        except Exception:

            logger.exception(
                "Error while validating Rule ID [%s]",
                row.get("Rule ID"),
            )

            raise

    # ==================================================================
    # Check Rule Cases
    # ==================================================================

    def _check_rule_cases(
        self,
        rule_cases_df: pd.DataFrame,
        rule_id: str,
    ) -> bool:
        """
        Search Rule ID in all Rule Cases columns.
        """

        logger.debug(
            "Checking Rule Cases for Rule ID [%s]",
            rule_id,
        )

        for column in rule_cases_df.columns:

            if (
                rule_cases_df[column]
                .astype(str)
                .str.strip()
                .eq(rule_id)
                .any()
            ):

                return True

        return False

    # ==================================================================
    # Check Skipped Rule
    # ==================================================================

    def _is_skipped_rule(
        self,
        row: pd.Series,
    ) -> bool:
        """
        Determine whether a rule is skipped.

        Current logic:
            Total Findings == 0
        """

        try:

            findings = int(
                row["Total Findings"]
            )

            return findings == 0

        except Exception:

            logger.warning(
                "Unable to determine skipped rule for Rule ID [%s]",
                row["Rule ID"],
            )

            return False
        
    # ==================================================================
    # Build Remarks
    # ==================================================================

    def _build_remarks(
        self,
        issue_present: bool,
        p21_rule_present: bool,
        study_present: bool,
        test_case_present: bool,
        rule_cases_present: bool,
        domain_match: bool,
        skipped_rule: bool,
    ) -> str:
        """
        Build validation remarks.

        Returns
        -------
        str
            Validation remarks.
        """

        remarks = []

        if skipped_rule:
            remarks.append("Skipped Rule")

        if not issue_present:
            remarks.append("Rule ID missing in P21 Issue Summary")

        if not p21_rule_present:
            remarks.append("Rule ID missing in P21 Rules")

        if not study_present:
            remarks.append("Rule ID missing in SDTMIG Study")

        if not test_case_present:
            remarks.append("Rule ID missing in SDTMIG Test Case")

        if not rule_cases_present:
            remarks.append("Rule ID missing in SDTMIG Rule Cases")

        if not domain_match:
            remarks.append("Domain mismatch")

        if not remarks:
            return "All validations passed"

        return "; ".join(remarks)
    
    # ==================================================================
    # Check Required Columns
    # ==================================================================

    def _check_required_columns(
        self,
        df: pd.DataFrame,
        required_columns: list[str],
        sheet_name: str,
    ) -> None:
        """
        Validate required columns in a worksheet.

        Parameters
        ----------
        df : DataFrame
            Worksheet.

        required_columns : list
            Mandatory columns.

        sheet_name : str
            Excel sheet name.
        """

        logger.info(
            "Validating required columns for sheet [%s]",
            sheet_name,
        )

        missing_columns = [

            column

            for column in required_columns

            if column not in df.columns

        ]

        if missing_columns:

            logger.error(
                "Missing columns in [%s]: %s",
                sheet_name,
                ", ".join(missing_columns),
            )

            raise ValueError(
                f"Missing columns in sheet '{sheet_name}' : "
                f"{', '.join(missing_columns)}"
            )

        logger.info(
            "All required columns are present in [%s]",
            sheet_name,
        )