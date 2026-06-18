from pathlib import Path

import pandas as pd

from app.core.config import DEFAULT_OUTPUT_FILE


class ReportWriter:
    """Generate Excel report with batch-wise replace and append logic."""

    def write_report(
        self,
        rule_results: pd.DataFrame,
        imputation_results: pd.DataFrame,
        missing_rules: pd.DataFrame,
        count_mismatches: pd.DataFrame,
        skipped_rules: pd.DataFrame,
        batch_summary: pd.DataFrame,
        batch_name: str,
        output_path: Path = DEFAULT_OUTPUT_FILE,
    ) -> str:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        sheets_data = {
            "Rule Validation Results": rule_results,
            "Imputation Results": imputation_results,
            "Missing P21 Rules": missing_rules,
            "Count Mismatches": count_mismatches,
            "Skipped Rules": skipped_rules,
            "Batch Summary": batch_summary,
        }

        existing_data = {}

        if output_path.exists():
            existing_data = pd.read_excel(output_path, sheet_name=None)

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for sheet_name, new_df in sheets_data.items():
                if sheet_name in existing_data:
                    old_df = existing_data[sheet_name]

                    if "Batch Name" in old_df.columns:
                        old_df = old_df[
                            old_df["Batch Name"].astype(str) != str(batch_name)
                        ]

                    final_df = pd.concat(
                        [old_df, new_df],
                        ignore_index=True,
                    )
                else:
                    final_df = new_df

                final_df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                )
                worksheet = writer.sheets[sheet_name]
                worksheet.freeze_panes = "A2"

        return str(output_path)