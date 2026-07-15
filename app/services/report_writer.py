from pathlib import Path

import pandas as pd

# from app.core.config import DEFAULT_OUTPUT_FILE


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
        output_path: Path = None
    ) -> str:
        
        if output_path is None:
            output_path = DEFAULT_OUTPUT_FILE

        # Create folder if it doesn't exist
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Delete old validation report
        if output_path.exists():
            output_path.unlink()


        sheets_data = {
            "Rule Validation Results": rule_results,
            "Imputation Results": imputation_results,
            "Missing P21 Rules": missing_rules,
            "Count Mismatches": count_mismatches,
            "Skipped Rules": skipped_rules,
            "Batch Summary": batch_summary,
        }

        with pd.ExcelWriter(
            output_path,
            engine="openpyxl",
        ) as writer:

            for sheet_name, df in sheets_data.items():

                df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
            )

            worksheet = writer.sheets[sheet_name]

            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
                

        return str(output_path)