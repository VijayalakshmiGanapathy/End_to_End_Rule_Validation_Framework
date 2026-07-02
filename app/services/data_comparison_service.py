import json
import re
from pathlib import Path

import pandas as pd

from app.core.config import ROW_INDEX_OFFSET, SDTM_DOMAINS


class DataComparisonService:
    """Validate original vs dirty CSV using injection audit details."""

    def _extract_row_count(self, text: str) -> int:
        match = re.search(r"(\d+)\s*rows?", str(text))
        return int(match.group(1)) if match else 0

    def compare_original_dirty(
        self,
        original_data_dir: str,
        dirty_data_dir: str,
        export_detail_df: pd.DataFrame,
    ) -> pd.DataFrame:
        results = []

        original_dir = Path(original_data_dir)
        dirty_dir = Path(dirty_data_dir)

        export_detail_df.columns = export_detail_df.columns.str.strip()
        csv_cache = {}

        for index, (_, detail_row) in enumerate(export_detail_df.iterrows()):
            if index % 50 == 0:
                print(
                    f"Processing row {index + 1}/{len(export_detail_df)} | "
                    f"Rule={detail_row.get('rule_id')} | "
                    f"Domain={detail_row.get('domain')}"
                )

            rule_id = str(detail_row.get("rule_id", "")).strip()
            error_id = str(detail_row.get("error_id", "")).strip()
            domain = str(detail_row.get("domain", "")).strip()
            usubjid = str(detail_row.get("USUBJID", "")).strip()
            primitive = str(detail_row.get("primitive", "")).strip().lower()

            status = str(detail_row.get("status", "")).strip().lower()

            if status == "failed_self_validation":
                results.append(
                    {
                        "Rule ID": rule_id,
                        "Error ID": error_id,
                        "Audit Domain": domain,
                        "Target Domain": domain,
                        "USUBJID": usubjid,
                        "Variable": "",
                        "Original and Dirty csv imputation match": "No",
                        "Validation Status": "SELF VALIDATION FAILED",
                        "Comments": str(
                            detail_row.get("failure_reason", "")
                        ).strip(),
                    }
                )
                continue

            try:
                variables_modified = json.loads(
                    str(detail_row.get("variables_modified", "{}"))
                )
            except json.JSONDecodeError:
                results.append(
                    {
                        "Rule ID": rule_id,
                        "Error ID": error_id,
                        "Audit Domain": domain,
                        "Target Domain": "",
                        "USUBJID": usubjid,
                        "Original and Dirty csv imputation match": "No",
                        "Validation Status": "FAIL",
                        "Comments": "Unable to parse variables_modified",
                    }
                )
                continue

            target_domain = self._get_target_domain(
                audit_domain=domain,
                variables_modified=variables_modified,
            )

            original_file = original_dir / f"{target_domain}.csv"
            dirty_file = dirty_dir / f"{target_domain}.csv"

            if not original_file.exists() or not dirty_file.exists():
                results.append(
                    {
                        "Rule ID": rule_id,
                        "Error ID": error_id,
                        "Audit Domain": domain,
                        "Target Domain": target_domain,
                        "USUBJID": usubjid,
                        "Original and Dirty csv imputation match": "No",
                        "Validation Status": "FAIL",
                        "Comments": (
                            f"{target_domain}.csv missing in original "
                            "or dirty folder"
                        ),
                    }
                )
                continue

            if target_domain not in csv_cache:
                csv_cache[target_domain] = (
                    pd.read_csv(
                        original_file,
                        dtype=str,
                        keep_default_na=False,
                    ).apply(lambda col: col.str.strip()),
                    pd.read_csv(
                        dirty_file,
                        dtype=str,
                        keep_default_na=False,
                    ).apply(lambda col: col.str.strip()),
                )

            original_df, dirty_df = csv_cache[target_domain]

            row_index_value = detail_row.get("row_index", "")
            row_index = None
            csv_row_number = ""
            pandas_index = None

            if not pd.isna(row_index_value) and str(row_index_value).strip() != "":
                row_index = int(float(row_index_value))
                csv_row_number = row_index + ROW_INDEX_OFFSET
                pandas_index = row_index

            for variable, values in variables_modified.items():
                variable = str(variable).strip()

                expected_original = self._normalize_value(
                    values.get("original", "")
                )
                expected_injected = self._normalize_value(
                    values.get("injected", "")
                )

                # Handles Batch 14 TS case:
                # {"TSPARMCD": {"original": "TITLE", "injected": "(row deleted)"}}
                if expected_injected.lower() == "(row deleted)":
                    results.append(
                        self._validate_row_deleted_by_key_value(
                            rule_id=rule_id,
                            error_id=error_id,
                            audit_domain=domain,
                            target_domain=target_domain,
                            usubjid=usubjid,
                            variable=variable,
                            expected_original=expected_original,
                            row_index=row_index,
                            csv_row_number=csv_row_number,
                            pandas_index=pandas_index,
                            original_df=original_df,
                            dirty_df=dirty_df,
                        )
                    )
                    continue

                if primitive == "delete_row":
                    results.append(
                        self._validate_delete_row_by_index(
                            rule_id=rule_id,
                            error_id=error_id,
                            audit_domain=domain,
                            target_domain=target_domain,
                            usubjid=usubjid,
                            row_index=row_index,
                            csv_row_number=csv_row_number,
                            pandas_index=pandas_index,
                            original_df=original_df,
                            dirty_df=dirty_df,
                        )
                    )
                    continue

                if (
                    variable.upper() == target_domain.upper()
                    and "rows" in str(values).lower()
                ):
                    results.append(
                        self._validate_row_count_change(
                            rule_id=rule_id,
                            error_id=error_id,
                            audit_domain=domain,
                            target_domain=target_domain,
                            usubjid=usubjid,
                            variable=variable,
                            values=values,
                            original_df=original_df,
                            dirty_df=dirty_df,
                        )
                    )
                    continue

                if variable == "__row__":
                    if pandas_index is None:
                        results.append(
                            self._failure_row(
                                rule_id,
                                error_id,
                                domain,
                                target_domain,
                                usubjid,
                                variable,
                                csv_row_number,
                                "row_index missing for duplicate row validation",
                            )
                        )
                        continue

                    results.append(
                        self._validate_duplicate_row(
                            rule_id=rule_id,
                            error_id=error_id,
                            audit_domain=domain,
                            target_domain=target_domain,
                            usubjid=usubjid,
                            row_index=row_index,
                            csv_row_number=csv_row_number,
                            pandas_index=pandas_index,
                            original_df=original_df,
                            dirty_df=dirty_df,
                        )
                    )
                    continue

                if pandas_index is None:
                    results.append(
                        self._validate_using_usubjid(
                            rule_id=rule_id,
                            error_id=error_id,
                            audit_domain=domain,
                            target_domain=target_domain,
                            usubjid=usubjid,
                            variable=variable,
                            expected_original=expected_original,
                            expected_injected=expected_injected,
                            original_df=original_df,
                            dirty_df=dirty_df,
                        )
                    )
                    continue

                if variable not in original_df.columns:
                    if variable in dirty_df.columns:
                        actual_dirty = self._normalize_value(
                            dirty_df.iloc[pandas_index][variable]
                        )

                        dirty_match = self._values_match(
                            actual_dirty,
                            expected_injected,
                        )

                        results.append(
                            {
                                "Rule ID": rule_id,
                                "Error ID": error_id,
                                "Audit Domain": domain,
                                "Target Domain": target_domain,
                                "USUBJID": usubjid,
                                "Variable": variable,
                                "Audit Row Index": row_index,
                                "CSV Row Index Checked": csv_row_number,
                                #"Pandas Index Checked": pandas_index,
                                "Expected Original Value": (
                                    "Column not present in original"
                                ),
                                "Actual Original Value": (
                                    "Column not present in original"
                                ),
                                "Expected Injected Value": expected_injected,
                                "Actual Dirty Value": actual_dirty,
                                "Original Match": "Yes",
                                "Dirty Match": "Yes" if dirty_match else "No",
                                "Original and Dirty csv imputation match": (
                                    "Yes" if dirty_match else "No"
                                ),
                                "Validation Status": (
                                    "PASS" if dirty_match else "FAIL"
                                ),
                                "Comments": (
                                    "New column injection verified successfully"
                                    if dirty_match
                                    else "New column injection mismatch"
                                ),
                            }
                        )
                        continue

                    results.append(
                        self._failure_row(
                            rule_id,
                            error_id,
                            domain,
                            target_domain,
                            usubjid,
                            variable,
                            csv_row_number,
                            f"{variable} not found in original or dirty CSV",
                        )
                    )
                    continue

                if variable not in dirty_df.columns:
                    results.append(
                        self._failure_row(
                            rule_id,
                            error_id,
                            domain,
                            target_domain,
                            usubjid,
                            variable,
                            csv_row_number,
                            f"{variable} not found in dirty CSV",
                        )
                    )
                    continue

                if pandas_index >= len(original_df) or pandas_index >= len(dirty_df):
                    results.append(
                        self._failure_row(
                            rule_id,
                            error_id,
                            domain,
                            target_domain,
                            usubjid,
                            variable,
                            csv_row_number,
                            "Row index out of range",
                        )
                    )
                    continue

                actual_original = self._normalize_value(
                    original_df.iloc[pandas_index][variable]
                )
                actual_dirty = self._normalize_value(
                    dirty_df.iloc[pandas_index][variable]
                )

                if rule_id == "SD1380":
                    print("SD1380 DEBUG")
                    print("row_index:", row_index)
                    print("csv_row_number:", csv_row_number)
                    print("pandas_index:", pandas_index)
                    print("variable:", variable)
                    print("expected_original:", expected_original)
                    print("actual_original:", actual_original)
                    print("expected_injected:", expected_injected)
                    print("actual_dirty:", actual_dirty)

                original_match = self._values_match(
                    actual_original,
                    expected_original,
                )
                dirty_match = self._values_match(
                    actual_dirty,
                    expected_injected,
                )

                imputation_match = original_match and dirty_match

                results.append(
                    {
                        "Rule ID": rule_id,
                        "Error ID": error_id,
                        "Audit Domain": domain,
                        "Target Domain": target_domain,
                        "USUBJID": usubjid,
                        "Variable": variable,
                        "Audit Row Index": row_index,
                        "CSV Row Index Checked": csv_row_number,
                        #"Pandas Index Checked": pandas_index,
                        "Expected Original Value": expected_original,
                        "Actual Original Value": actual_original,
                        "Expected Injected Value": expected_injected,
                        "Actual Dirty Value": actual_dirty,
                        "Original Match": "Yes" if original_match else "No",
                        "Dirty Match": "Yes" if dirty_match else "No",
                        "Original and Dirty csv imputation match": (
                            "Yes" if imputation_match else "No"
                        ),
                        "Validation Status": (
                            "PASS" if imputation_match else "FAIL"
                        ),
                        "Comments": (
                            "Imputation verified successfully"
                            if imputation_match
                            else "Original or dirty value mismatch"
                        ),
                    }
                )

        results_df = pd.DataFrame(results)

        return results_df

    def _get_target_domain(
        self,
        audit_domain: str,
        variables_modified: dict,
    ) -> str:
        for key in variables_modified.keys():
            key = str(key).strip().upper()
            if key in SDTM_DOMAINS:
                return key

        return audit_domain.strip().upper()

    def _validate_row_deleted_by_key_value(
        self,
        rule_id: str,
        error_id: str,
        audit_domain: str,
        target_domain: str,
        usubjid: str,
        variable: str,
        expected_original: str,
        row_index: int | None,
        csv_row_number: int | str,
        pandas_index: int | None,
        original_df: pd.DataFrame,
        dirty_df: pd.DataFrame,
    ) -> dict:
        if variable not in original_df.columns:
            return self._failure_row(
                rule_id,
                error_id,
                audit_domain,
                target_domain,
                usubjid,
                variable,
                csv_row_number,
                f"{variable} not found in original CSV",
            )

        if variable not in dirty_df.columns:
            return self._failure_row(
                rule_id,
                error_id,
                audit_domain,
                target_domain,
                usubjid,
                variable,
                csv_row_number,
                f"{variable} not found in dirty CSV",
            )

        original_matches = original_df[
            original_df[variable]
            .astype(str)
            .str.strip()
            .eq(expected_original)
        ]

        dirty_matches = dirty_df[
            dirty_df[variable]
            .astype(str)
            .str.strip()
            .eq(expected_original)
        ]

        original_exists = not original_matches.empty
        dirty_exists = not dirty_matches.empty
        imputation_match = original_exists and not dirty_exists

        return {
            "Rule ID": rule_id,
            "Error ID": error_id,
            "Audit Domain": audit_domain,
            "Target Domain": target_domain,
            "USUBJID": usubjid,
            "Variable": variable,
            "Audit Row Index": row_index,
            "CSV Row Index Checked": csv_row_number,
            #"Pandas Index Checked": pandas_index,
            "Expected Original Value": (
                f"Row where {variable}={expected_original}"
            ),
            "Actual Original Value": (
                "Row present in original"
                if original_exists
                else "Row not present in original"
            ),
            "Expected Injected Value": "Entire row deleted",
            "Actual Dirty Value": (
                "Row still present in dirty"
                if dirty_exists
                else "Entire row deleted from dirty"
            ),
            "Original Match": "Yes" if original_exists else "No",
            "Dirty Match": "Yes" if not dirty_exists else "No",
            "Original and Dirty csv imputation match": (
                "Yes" if imputation_match else "No"
            ),
            "Validation Status": "PASS" if imputation_match else "FAIL",
            "Comments": (
                f"Entire row containing {variable}={expected_original} "
                "deleted successfully"
                if imputation_match
                else (
                    f"Entire row containing {variable}={expected_original} "
                    "was not deleted correctly"
                )
            ),
        }

    def _validate_delete_row_by_index(
        self,
        rule_id: str,
        error_id: str,
        audit_domain: str,
        target_domain: str,
        usubjid: str,
        row_index: int | None,
        csv_row_number: int | str,
        pandas_index: int | None,
        original_df: pd.DataFrame,
        dirty_df: pd.DataFrame,
    ) -> dict:
        if pandas_index is None:
            return self._failure_row(
                rule_id,
                error_id,
                audit_domain,
                target_domain,
                usubjid,
                "__row_deleted__",
                csv_row_number,
                "row_index missing for delete_row validation",
            )

        if pandas_index >= len(original_df):
            return self._failure_row(
                rule_id,
                error_id,
                audit_domain,
                target_domain,
                usubjid,
                "__row_deleted__",
                csv_row_number,
                "Row index out of range for delete_row validation",
            )

        original_row = original_df.iloc[pandas_index].astype(str).str.strip()

        common_columns = [
            col for col in original_df.columns if col in dirty_df.columns
        ]

        row_exists_in_dirty = (
            dirty_df[common_columns]
            .astype(str)
            .apply(lambda col: col.str.strip())
            .eq(original_row[common_columns])
            .all(axis=1)
            .any()
        )

        imputation_match = not row_exists_in_dirty

        return {
            "Rule ID": rule_id,
            "Error ID": error_id,
            "Audit Domain": audit_domain,
            "Target Domain": target_domain,
            "USUBJID": usubjid,
            "Variable": "__row_deleted__",
            "Audit Row Index": row_index,
            "CSV Row Index Checked": csv_row_number,
            #"Pandas Index Checked": pandas_index,
            "Expected Original Value": "Row present in original",
            "Actual Original Value": "Present",
            "Expected Injected Value": "Row removed from dirty",
            "Actual Dirty Value": (
                "Still present" if row_exists_in_dirty else "Removed"
            ),
            "Original Match": "Yes",
            "Dirty Match": "Yes" if imputation_match else "No",
            "Original and Dirty csv imputation match": (
                "Yes" if imputation_match else "No"
            ),
            "Validation Status": "PASS" if imputation_match else "FAIL",
            "Comments": (
                "Delete row imputation verified successfully"
                if imputation_match
                else "Deleted row still exists in dirty CSV"
            ),
        }

    def _validate_row_count_change(
        self,
        rule_id: str,
        error_id: str,
        audit_domain: str,
        target_domain: str,
        usubjid: str,
        variable: str,
        values: dict,
        original_df: pd.DataFrame,
        dirty_df: pd.DataFrame,
    ) -> dict:
        expected_original_text = self._normalize_value(values.get("original", ""))
        expected_injected_text = self._normalize_value(values.get("injected", ""))

        expected_original_count = self._extract_row_count(expected_original_text)
        expected_dirty_count = self._extract_row_count(expected_injected_text)

        actual_original_count = len(original_df)
        actual_dirty_count = len(dirty_df)

        original_match = actual_original_count >= expected_original_count
        dirty_match = actual_dirty_count <= expected_dirty_count
        imputation_match = dirty_match

        return {
            "Rule ID": rule_id,
            "Error ID": error_id,
            "Audit Domain": audit_domain,
            "Target Domain": target_domain,
            "USUBJID": usubjid,
            "Variable": variable,
            "Audit Row Index": "",
            "CSV Row Index Checked": "",
            #"Pandas Index Checked": "",
            "Expected Original Value": expected_original_text,
            "Actual Original Value": f"{actual_original_count} rows",
            "Expected Injected Value": expected_injected_text,
            "Actual Dirty Value": f"{actual_dirty_count} rows",
            "Original Match": "Yes" if original_match else "No",
            "Dirty Match": "Yes" if dirty_match else "No",
            "Original and Dirty csv imputation match": (
                "Yes" if imputation_match else "No"
            ),
            "Validation Status": "PASS" if imputation_match else "FAIL",
            "Comments": (
                "Cumulative row-count validation accepted"
                if imputation_match
                else "Cumulative row-count mismatch"
            ),
        }

    def _validate_duplicate_row(
        self,
        rule_id: str,
        error_id: str,
        audit_domain: str,
        target_domain: str,
        usubjid: str,
        row_index: int,
        csv_row_number: int,
        pandas_index: int,
        original_df: pd.DataFrame,
        dirty_df: pd.DataFrame,
    ) -> dict:
        if "USUBJID" not in original_df.columns or "USUBJID" not in dirty_df.columns:
            return self._failure_row(
                rule_id,
                error_id,
                audit_domain,
                target_domain,
                usubjid,
                "__row__",
                csv_row_number,
                "USUBJID column missing for duplicate row validation",
            )

        if (
            target_domain.upper() == "SV"
            and "VISITNUM" in original_df.columns
            and "VISITNUM" in dirty_df.columns
            and pandas_index < len(original_df)
        ):
            visitnum = self._normalize_value(
                original_df.iloc[pandas_index]["VISITNUM"]
            )

            original_count = (
                (
                    original_df["USUBJID"].astype(str).str.strip()
                    == usubjid
                )
                & (
                    original_df["VISITNUM"].astype(str).str.strip()
                    == visitnum
                )
            ).sum()

            dirty_count = (
                (
                    dirty_df["USUBJID"].astype(str).str.strip()
                    == usubjid
                )
                & (
                    dirty_df["VISITNUM"].astype(str).str.strip()
                    == visitnum
                )
            ).sum()

            duplicate_key = f"USUBJID={usubjid}, VISITNUM={visitnum}"

        else:
            original_count = (
                original_df["USUBJID"].astype(str).str.strip() == usubjid
            ).sum()

            dirty_count = (
                dirty_df["USUBJID"].astype(str).str.strip() == usubjid
            ).sum()

            duplicate_key = f"USUBJID={usubjid}"

        original_match = original_count == 1
        dirty_match = dirty_count > 1
        imputation_match = original_match and dirty_match

        return {
            "Rule ID": rule_id,
            "Error ID": error_id,
            "Audit Domain": audit_domain,
            "Target Domain": target_domain,
            "USUBJID": usubjid,
            "Variable": "__row__",
            "Audit Row Index": row_index,
            "CSV Row Index Checked": csv_row_number,
            #"Pandas Index Checked": pandas_index,
            "Expected Original Value": "unique",
            "Actual Original Value": f"{duplicate_key}; count={original_count}",
            "Expected Injected Value": "duplicated",
            "Actual Dirty Value": f"{duplicate_key}; count={dirty_count}",
            "Original Match": "Yes" if original_match else "No",
            "Dirty Match": "Yes" if dirty_match else "No",
            "Original and Dirty csv imputation match": (
                "Yes" if imputation_match else "No"
            ),
            "Validation Status": "PASS" if imputation_match else "FAIL",
            "Comments": (
                "Duplicate row injection verified successfully"
                if imputation_match
                else "Duplicate row injection mismatch"
            ),
        }

    def _validate_using_usubjid(
        self,
        rule_id: str,
        error_id: str,
        audit_domain: str,
        target_domain: str,
        usubjid: str,
        variable: str,
        expected_original: str,
        expected_injected: str,
        original_df: pd.DataFrame,
        dirty_df: pd.DataFrame,
    ) -> dict:
        if "USUBJID" not in original_df.columns or "USUBJID" not in dirty_df.columns:
            return self._failure_row(
                rule_id,
                error_id,
                audit_domain,
                target_domain,
                usubjid,
                variable,
                "",
                "row_index missing and USUBJID column unavailable",
            )

        original_rows = original_df[
            original_df["USUBJID"].astype(str).str.strip() == usubjid
        ]

        dirty_rows = dirty_df[
            dirty_df["USUBJID"].astype(str).str.strip() == usubjid
        ]

        if original_rows.empty or dirty_rows.empty:
            return self._failure_row(
                rule_id,
                error_id,
                audit_domain,
                target_domain,
                usubjid,
                variable,
                "",
                "USUBJID not found in original or dirty CSV",
            )

        if variable not in original_rows.columns or variable not in dirty_rows.columns:
            return self._failure_row(
                rule_id,
                error_id,
                audit_domain,
                target_domain,
                usubjid,
                variable,
                "",
                f"{variable} not found while validating with USUBJID",
            )

        actual_original = self._normalize_value(original_rows.iloc[0][variable])
        actual_dirty = self._normalize_value(dirty_rows.iloc[0][variable])

        original_match = self._values_match(actual_original, expected_original)
        dirty_match = self._values_match(actual_dirty, expected_injected)
        imputation_match = original_match and dirty_match

        return {
            "Rule ID": rule_id,
            "Error ID": error_id,
            "Audit Domain": audit_domain,
            "Target Domain": target_domain,
            "USUBJID": usubjid,
            "Variable": variable,
            "Audit Row Index": "",
            "CSV Row Index Checked": "",
            #"Pandas Index Checked": "",
            "Expected Original Value": expected_original,
            "Actual Original Value": actual_original,
            "Expected Injected Value": expected_injected,
            "Actual Dirty Value": actual_dirty,
            "Original Match": "Yes" if original_match else "No",
            "Dirty Match": "Yes" if dirty_match else "No",
            "Original and Dirty csv imputation match": (
                "Yes" if imputation_match else "No"
            ),
            "Validation Status": "PASS" if imputation_match else "FAIL",
            "Comments": (
                "USUBJID-based validation successful"
                if imputation_match
                else "USUBJID-based value mismatch"
            ),
        }

    def _failure_row(
        self,
        rule_id: str,
        error_id: str,
        audit_domain: str,
        target_domain: str,
        usubjid: str,
        variable: str,
        csv_row_number: int | str,
        comments: str,
    ) -> dict:
        return {
            "Rule ID": rule_id,
            "Error ID": error_id,
            "Audit Domain": audit_domain,
            "Target Domain": target_domain,
            "USUBJID": usubjid,
            "Variable": variable,
            "CSV Row Index Checked": csv_row_number,
            "Original and Dirty csv imputation match": "No",
            "Validation Status": "FAIL",
            "Comments": comments,
        }

    def _normalize_value(self, value: object) -> str:
        value = "" if pd.isna(value) else str(value).strip()

        if not self._looks_like_date(value):
            return value

        for date_format in ("%Y-%m-%d", "%d-%m-%Y"):
            parsed_date = pd.to_datetime(
                value,
                format=date_format,
                errors="coerce",
            )

            if pd.notna(parsed_date):
                return parsed_date.strftime("%Y-%m-%d")

        return value

    def _values_match(self, actual: str, expected: str) -> bool:
        return self._normalize_value(actual) == self._normalize_value(expected)

    def _looks_like_date(self, value: str) -> bool:
        return "-" in value and len(value) >= 8