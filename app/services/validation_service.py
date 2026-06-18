import logging

import pandas as pd

from app.core.config import ISSUE_SUMMARY_SHEET, P21_RULES_SHEET, IMPUTATION_MATCH_THRESHOLD
from app.models.validation_request import ValidationRequest
from app.services.data_comparison_service import DataComparisonService
from app.services.report_writer import ReportWriter
from app.utils.file_reader import read_csv_file, read_excel_sheet



logger = logging.getLogger(__name__)


class ValidationService:
    """Main validation orchestration service."""

    def __init__(self, request: ValidationRequest) -> None:
        self.request = request
        self.report_writer = ReportWriter()
        self.data_comparison_service = DataComparisonService()

    def run_validation(self) -> str:
        logger.info(
            "Starting validation for batch=%s host_generator_key=%s",
            self.request.batch_name,
            self.request.host_generator_key,
        )

        export_summary_df = read_csv_file(self.request.export_summary_path)
        export_detail_df = read_csv_file(self.request.export_detail_path)
        
        export_summary_df.columns = export_summary_df.columns.str.strip()
        export_detail_df.columns = export_detail_df.columns.str.strip()

        logger.info("Export summary columns: %s", export_summary_df.columns.tolist())
        logger.info("Export detail columns: %s", export_detail_df.columns.tolist())

        p21_issue_df = read_excel_sheet(
            self.request.p21_report_path,
            ISSUE_SUMMARY_SHEET,
        )

        p21_issue_df.columns = p21_issue_df.columns.str.strip()

        p21_issue_df["Source"] = p21_issue_df["Source"].ffill()

        p21_issue_df["Source"] = (
            p21_issue_df["Source"]
            .astype(str)
            .str.replace(".xpt", "", regex=False)
            .str.strip()
            .str.upper()
        )

        p21_issue_df["Pinnacle 21 ID"] = (
            p21_issue_df["Pinnacle 21 ID"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        p21_rules_df = read_excel_sheet(
            self.request.p21_report_path,
            P21_RULES_SHEET,
        )

        p21_issue_df.columns = p21_issue_df.columns.str.strip()
        p21_rules_df.columns = p21_rules_df.columns.str.strip()

        # logger.info("P21 Issue Summary columns: %s", p21_issue_df.columns.tolist())
        # logger.info("P21 Rules columns: %s", p21_rules_df.columns.tolist())

        p21_rules_df.columns = p21_rules_df.columns.str.strip()
        # logger.info("P21 Rules columns: %s", p21_rules_df.columns.tolist())

        

        working_rules_df = pd.read_excel(
            self.request.working_rules_path,
            sheet_name="15 Batches",
        )

        working_rules_df.columns = working_rules_df.columns.str.strip()

        working_rules_df["Batch"] = (
            working_rules_df["Batch"]
                .astype(str)
                .str.strip()
            )

        working_rules_df["Host Generator Key"] = (
            working_rules_df["Host Generator Key"]
                .astype(str)
                .str.strip()
            )

        working_rules_df["Rule ID"] = (
            working_rules_df["Rule ID"]
            .astype(str)
            .str.strip()
        )

        print("========== WORKING RULES DEBUG ==========")
        print("Requested Batch:", repr(self.request.batch_name))
        print("Requested Host Generator Key:", repr(self.request.host_generator_key))

        print(
            working_rules_df[
                ["Batch", "Host Generator Key", "Rule ID"]
            ].head(20)
        )

        working_rules_df = working_rules_df[
            working_rules_df["Batch"].str.contains(
                self.request.batch_name,
                case=False,
                na=False,
                regex=False,
            )
            & (
                working_rules_df["Host Generator Key"].str.lower()
                == self.request.host_generator_key.lower()
            )
        ]

        print("Filtered working_rules_df row count:", len(working_rules_df))

        if not working_rules_df.empty:
            print(
                working_rules_df[
                    ["Batch", "Host Generator Key", "Rule ID"]
                ]
            )

        test_case_sheets = pd.read_excel(
            self.request.test_case_path,
            sheet_name=None,
        )

        logger.info("Starting Original vs Dirty comparison...")

        imputation_results = (
            self.data_comparison_service.compare_original_dirty(
                self.request.original_data_dir,
                self.request.dirty_data_dir,
                export_detail_df,
            )
        )

        logger.info("Original vs Dirty comparison completed.")

        logger.info("Building rule validation results...")

        rule_results = self._build_rule_results(
            export_summary_df=export_summary_df,
            export_detail_df=export_detail_df,
            p21_issue_df=p21_issue_df,
            p21_rules_df=p21_rules_df,
            working_rules_df=working_rules_df,
            test_case_sheets=test_case_sheets,
            imputation_results=imputation_results,
        )

        logger.info("Rule validation results built successfully.")


        skipped_rules = self._build_skipped_rules(
            working_rules_df=working_rules_df,
            export_summary_df=export_summary_df,
            p21_issue_df=p21_issue_df,
            p21_rules_df=p21_rules_df,
            test_case_sheets=test_case_sheets,
            
        )

        missing_rules = rule_results[
            rule_results["Rule present in P21 Issue Summary"] == "No"
        ].copy()

        count_mismatches = rule_results[
            rule_results["Count Match"] == "No"
        ].copy()

        batch_summary = self._build_batch_summary(rule_results)

        logger.info("Starting Excel report generation...")


        output_path = self.report_writer.write_report(
            rule_results=rule_results,
            imputation_results=imputation_results,
            missing_rules=missing_rules,
            count_mismatches=count_mismatches,
            skipped_rules=skipped_rules,
            batch_summary=batch_summary,
            batch_name=self.request.batch_name,

        )

        logger.info("Excel report generated successfully.")
        

        logger.info("Validation completed. Report generated: %s", output_path)
        return output_path

    def _build_rule_results(
        self,
        export_summary_df: pd.DataFrame,
        export_detail_df: pd.DataFrame,
        p21_issue_df: pd.DataFrame,
        p21_rules_df: pd.DataFrame,
        working_rules_df: pd.DataFrame,
        test_case_sheets: dict[str, pd.DataFrame],
        imputation_results: pd.DataFrame,
    ) -> pd.DataFrame:
        """Build rule-level validation result rows using exact columns."""

        rule_ids = self._extract_rule_ids(export_summary_df)
        rows = []

        for rule_id in rule_ids:
            detail_rows = self._filter_export_detail_by_rule(
                export_detail_df,
                rule_id,
            )

            working_rule_rows = self._filter_working_rules_by_rule(
                working_rules_df,
                rule_id,
            )

            p21_issue_rows = self._filter_p21_issue_by_rule(
                p21_issue_df,
                rule_id,
            )

            p21_rules_rows = self._filter_p21_rules_by_rule(
                p21_rules_df,
                rule_id,
            )

            domain_match = self._domain_match(
                detail_rows,
                p21_issue_rows,
            )

            if "Rule ID" not in imputation_results.columns:
                imputation_results["Rule ID"] = ""

            if "Original and Dirty csv imputation match" not in imputation_results.columns:
                imputation_results["Original and Dirty csv imputation match"] = "No"

            rule_imputation = imputation_results[
                imputation_results["Rule ID"].astype(str) == str(rule_id)
            ]

            total_count = len(rule_imputation)

            success_count = (
                rule_imputation[
                    rule_imputation[
                        "Original and Dirty csv imputation match"
                    ] == "Yes"
                ]
                .shape[0]
            )

            success_percentage = (
                (success_count / total_count) * 100
            ) if total_count > 0 else 0.0

            imputation_match = success_percentage >= IMPUTATION_MATCH_THRESHOLD

            domain = self._safe_first_value(detail_rows, "domain")
            expected_count = len(detail_rows)
            actual_count = self._get_p21_actual_count(p21_issue_rows)

            rule_present_in_issue = not p21_issue_rows.empty
            rule_present_in_rules = not p21_rules_rows.empty
            rule_in_batch = not working_rule_rows.empty
            count_match = expected_count == actual_count

            row = {
                "Batch Name": self.request.batch_name,
                "Host Generator Key": self.request.host_generator_key,
                "Rule ID": rule_id,
                "Domain": domain,
                "Rule in 15 Batches Sheet": "Yes" if rule_in_batch else "No",
                "Rule injected in Export Summary": self._is_rule_in_export_summary(
                    export_summary_df,
                    rule_id,
                ),
                "Rule details available in Audit Report": (
                    "Yes" if not detail_rows.empty else "No"
                ),
                "Original and Dirty csv imputation match": (
                    "Yes" if imputation_match else "No"
                ),
                "Injection Count Expected": expected_count,
                "P21 Count Actual": actual_count,
                "Rule present in P21 Issue Summary": (
                    "Yes" if rule_present_in_issue else "No"
                ),
                "Rule in P21 Rules Sheet": (
                    "Yes" if rule_present_in_rules else "No"
                ),
                "Domain Match": domain_match,
                "Count Match": "Yes" if count_match else "No",
                "Rule in Study Sheet": self._exists_in_test_sheet(
                    test_case_sheets,
                    "Study",
                    rule_id,
                ),
                "Rule in Test Case Sheet": self._exists_in_test_sheet(
                    test_case_sheets,
                    "Test Case",
                    rule_id,
                ),
                "Rule in Rule Cases Sheet": self._exists_in_rule_cases_sheet(
                    test_case_sheets,
                    rule_id,
                ),
                
                "Rule Skipped": self._is_rule_skipped(rule_id),
                "Validation Status": self._status(
                    detail_available=not detail_rows.empty,
                    rule_present_in_issue=rule_present_in_issue,
                    domain_match=domain_match,
                    imputation_match=imputation_match,
                ),
                "Comments": self._comments(
                    rule_in_batch=rule_in_batch,
                    detail_available=not detail_rows.empty,
                    rule_present_in_issue=rule_present_in_issue,
                    rule_present_in_rules=rule_present_in_rules,
                    count_match=count_match,
                ),
            }

            rows.append(row)

        return pd.DataFrame(rows)

    def _build_skipped_rules(
        self,
        working_rules_df: pd.DataFrame,
        export_summary_df: pd.DataFrame,
        p21_issue_df: pd.DataFrame,
        p21_rules_df: pd.DataFrame,
        test_case_sheets: dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        columns = [
            "Batch Name",
            "Host Generator Key",
            "Skipped Rule ID",
            "Rule in 15 Batches Sheet",
            "Rule present in Export Summary",
            "Rule present in P21 Issue Summary",
            "Rule in P21 Rules Sheet",
            "Rule in Study Sheet",
            "Rule in Test Case Sheet",
            "Rule in Rule Cases Sheet",
            "Validation Status",
            "Comments",
        ]

        def normalize_rule_id(series):
            return (
                series.dropna()
                .astype(str)
                .str.strip()
                .str.upper()
                .str.replace(".0", "", regex=False)
            )

        working_rule_ids = set(
            normalize_rule_id(working_rules_df["Rule ID"])
        )

        summary_rule_ids = set(
            normalize_rule_id(export_summary_df["rule_id"])
        )

        skipped_rule_ids = sorted(working_rule_ids - summary_rule_ids)

        print("DEBUG Working Rule IDs:", sorted(working_rule_ids))
        print("DEBUG Summary Rule IDs:", sorted(summary_rule_ids))
        print("DEBUG Skipped Rule IDs:", skipped_rule_ids)

        rows = []

        for rule_id in skipped_rule_ids:
            working_rule_rows = self._filter_working_rules_by_rule(
                working_rules_df,
                rule_id,
            )

            p21_issue_rows = self._filter_p21_issue_by_rule(
                p21_issue_df,
                rule_id,
            )

            p21_rules_rows = self._filter_p21_rules_by_rule(
                p21_rules_df,
                rule_id,
            )

            rows.append(
                {
                    "Batch Name": self.request.batch_name,
                    "Host Generator Key": self.request.host_generator_key,
                    "Skipped Rule ID": rule_id,
                    "Rule in 15 Batches Sheet": (
                        "Yes" if not working_rule_rows.empty else "No"
                    ),
                    "Rule present in Audit Report": "No",
                    "Rule present in Export Summary": "No",
                    "Rule present in P21 Issue Summary": (
                        "Yes" if not p21_issue_rows.empty else "No"
                    ),
                    "Rule in P21 Rules Sheet": (
                        "Yes" if not p21_rules_rows.empty else "No"
                    ),
                    "Rule in Study Sheet": self._exists_in_test_sheet(
                        test_case_sheets,
                        "Study",
                        rule_id,
                    ),
                    "Rule in Test Case Sheet": self._exists_in_test_sheet(
                        test_case_sheets,
                        "Test Case",
                        rule_id,
                    ),
                    "Rule in Rule Cases Sheet": self._exists_in_rule_cases_sheet(
                        test_case_sheets,
                        rule_id,
                    ),
                    "Validation Status": "Skipped in Error Imputation",
                    "Comments": (
                        "Rule is present in SDTM_P21 Working file for the selected "
                        "batch and host generator key, but not present in Export Summary."
                    ),
                }
            )

        return pd.DataFrame(rows, columns=columns)

    def _extract_rule_ids(self, export_summary_df: pd.DataFrame) -> list[str]:
        """Extract Rule IDs from Export File 1 using exact column."""
        return sorted(
            export_summary_df["rule_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

    def _filter_export_detail_by_rule(
        self,
        export_detail_df: pd.DataFrame,
        rule_id: str,
    ) -> pd.DataFrame:
        return export_detail_df[
            export_detail_df["rule_id"].astype(str).str.strip() == str(rule_id)
        ]

    def _filter_p21_issue_by_rule(
        self,
        p21_issue_df: pd.DataFrame,
        rule_id: str,
    ) -> pd.DataFrame:
        rule_id = str(rule_id).strip().upper()

        return p21_issue_df[
            p21_issue_df["Pinnacle 21 ID"] == rule_id
        ]

    def _filter_p21_rules_by_rule(
        self,
        p21_rules_df: pd.DataFrame,
        rule_id: str,
    ) -> pd.DataFrame:
        return p21_rules_df[
            p21_rules_df["Pinnacle 21 ID"].astype(str).str.strip()
            == str(rule_id)
        ]

    def _filter_working_rules_by_rule(
        self,
        working_rules_df: pd.DataFrame,
        rule_id: str,
    ) -> pd.DataFrame:
        rule_id = str(rule_id).strip().upper()

        return working_rules_df[
            working_rules_df["Rule ID"]
            .astype(str)
            .str.strip()
            .str.upper()
            == rule_id
        ]

    def _is_rule_in_export_summary(
        self,
        export_summary_df: pd.DataFrame,
        rule_id: str,
    ) -> str:
        rows = export_summary_df[
            export_summary_df["rule_id"].astype(str).str.strip() == str(rule_id)
        ]

        if rows.empty:
            return "No"

        injected_count = int(rows["injected"].fillna(0).iloc[0])
        return "Yes" if injected_count > 0 else "No"

    def _get_p21_actual_count(self, p21_issue_rows: pd.DataFrame) -> int:
        if p21_issue_rows.empty:
            return 0

        if "Found" not in p21_issue_rows.columns:
            return len(p21_issue_rows)

        return int(pd.to_numeric(p21_issue_rows["Found"], errors="coerce").fillna(0).sum())

    def _domain_match(
        self,
        detail_rows: pd.DataFrame,
        p21_issue_rows: pd.DataFrame,
        ) -> str:
        """Check whether Export Detail Rule ID + Domain is present in P21."""

        if detail_rows.empty or p21_issue_rows.empty:
            return "No"

        export_domains = set(
        detail_rows["domain"]
        .astype(str)
        .str.strip()
        .str.upper()
        )

        p21_domains = set(
            p21_issue_rows["Source"]
            .astype(str)
            .str.replace(".xpt", "", regex=False)
            .str.strip()
            .str.upper()
        )

        return "Yes" if export_domains.intersection(p21_domains) else "No"

    def _exists_in_test_sheet(
        self,
        sheets: dict[str, pd.DataFrame],
        sheet_name: str,
        rule_id: str,
    ) -> str:
        for name, df in sheets.items():
            if sheet_name.lower() in name.lower():
                if "Rule ID" not in df.columns:
                    return "Rule ID Column Missing"

                result = df[
                    df["Rule ID"].astype(str).str.strip() == str(rule_id)
                ]

                return "Yes" if not result.empty else "No"

        return "Sheet Not Found"

    def _exists_in_rule_cases_sheet(
        self,
        sheets: dict[str, pd.DataFrame],
        rule_id: str,
    ) -> str:
        rule_cases_df = sheets.get("Rule Cases")

        if rule_cases_df is None:
            return "Sheet Not Found"

        exists = (
            rule_cases_df.astype(str)
            .apply(lambda col: col.str.strip())
            .eq(str(rule_id))
            .any()
            .any()
        )

        return "Yes" if exists else "No"

    

    def _safe_first_value(self, df: pd.DataFrame, column: str) -> str:
        if column in df.columns and not df.empty:
            value = df[column].dropna()
            if not value.empty:
                return str(value.iloc[0]).strip()
        return ""

    def _is_rule_skipped(self, rule_id: str) -> str:
        if not self.request.skipped_rules_path:
            return "No"

        skipped_df = read_csv_file(self.request.skipped_rules_path)

        if "rule_id" in skipped_df.columns:
            exists = (
                skipped_df["rule_id"].astype(str).str.strip() == str(rule_id)
            ).any()
            return "Yes" if exists else "No"

        if "Rule ID" in skipped_df.columns:
            exists = (
                skipped_df["Rule ID"].astype(str).str.strip() == str(rule_id)
            ).any()
            return "Yes" if exists else "No"

        return "No"

    def _status(
        self,
        detail_available: bool,
        rule_present_in_issue: bool,
        domain_match: str,
        imputation_match: bool,
    ) -> str:
        if not detail_available:
            return "MANUAL REVIEW - Injection detail missing"

        if not imputation_match:
            return "FAIL - Imputation mismatch"

        if not rule_present_in_issue:
            return "FAIL - Missing in P21 Issue Summary"

        if domain_match != "Yes":
            return "FAIL - Domain mismatch"

        return "PASS"

    def _comments(
        self,
        rule_in_batch: bool,
        detail_available: bool,
        rule_present_in_issue: bool,
        rule_present_in_rules: bool,
        count_match: bool,
    ) -> str:
        comments = []

        if not rule_in_batch:
            comments.append("Rule ID not found in 15 Batches sheet.")

        if not detail_available:
            comments.append("Injection metadata not found in Export File 2.")

        if not rule_present_in_rules:
            comments.append("Rule ID not found in P21 Rules sheet.")

        if not rule_present_in_issue:
            comments.append("Rule ID not found in P21 Issue Summary.")

        if not count_match:
            comments.append("Expected injection count and P21 Found count mismatch.")

        if not comments:
            comments.append("Rule validation successful.")

        return " ".join(comments)

    def _build_batch_summary(self, rule_results: pd.DataFrame) -> pd.DataFrame:
        total_rules = len(rule_results)

        passed_rules = len(
            rule_results[rule_results["Validation Status"] == "PASS"]
        )

        failed_rules = len(
            rule_results[
                rule_results["Validation Status"].astype(str).str.startswith("FAIL")
            ]
        )

        manual_review = len(
            rule_results[
                rule_results["Validation Status"]
                .astype(str)
                .str.startswith("MANUAL REVIEW")
            ]
        )

        missing_in_p21 = len(
            rule_results[
                rule_results["Rule present in P21 Issue Summary"] == "No"
            ]
        )

        count_mismatches = len(
            rule_results[rule_results["Count Match"] == "No"]
        )

        skipped_rules = len(
            rule_results[rule_results["Rule Skipped"] == "Yes"]
        )

        pass_percentage = (
            round((passed_rules / total_rules) * 100, 2)
            if total_rules > 0
            else 0
        )

        return pd.DataFrame(
            [
                {
                    "Batch Name": self.request.batch_name,
                    "Host Generator Key": self.request.host_generator_key,
                    "Total Rules": total_rules,
                    "Passed Rules": passed_rules,
                    "Failed Rules": failed_rules,
                    "Rules Missing in P21": missing_in_p21,
                    "Count Mismatches": count_mismatches,
                    "Skipped Rules": skipped_rules,
                    "Manual Review Required": manual_review,
                    "Pass Percentage": pass_percentage,
                }
            ]
        )