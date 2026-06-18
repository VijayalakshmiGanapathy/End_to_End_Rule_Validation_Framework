import pandas as pd

from app.models.validation_request import ValidationRequest
from app.services.validation_service import ValidationService


def test_extract_rule_ids_from_rule_id_column():
    request = ValidationRequest(
        batch_name="B01_DM_dates",
        host_generator_key="oncology_nsclc",
        export_summary_path="dummy.csv",
        export_detail_path="dummy.csv",
        p21_report_path="dummy.xlsx",
        working_rules_path="dummy.xlsx",
        test_case_path="dummy.xlsx",
        original_data_dir="original",
        dirty_data_dir="dirty",
    )
    service = ValidationService(request)
    df = pd.DataFrame({"Rule ID": ["SD0001", "SD0002", "SD0001"]})

    result = service._extract_rule_ids(df)

    assert result == ["SD0001", "SD0002"]


def test_exists_in_df_returns_yes_for_existing_rule():
    request = ValidationRequest(
        batch_name="B01_DM_dates",
        host_generator_key="oncology_nsclc",
        export_summary_path="dummy.csv",
        export_detail_path="dummy.csv",
        p21_report_path="dummy.xlsx",
        working_rules_path="dummy.xlsx",
        test_case_path="dummy.xlsx",
        original_data_dir="original",
        dirty_data_dir="dirty",
    )
    service = ValidationService(request)
    df = pd.DataFrame({"Rule ID": ["SD0001"]})

    assert service._exists_in_df(df, "SD0001") == "Yes"
