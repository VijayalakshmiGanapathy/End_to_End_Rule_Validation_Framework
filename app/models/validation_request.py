from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    """Request model for validation execution."""

    batch_name: str = Field(..., example="B01_DM_dates")
    host_generator_key: str = Field(..., example="oncology_nsclc")
    export_summary_path: str
    export_detail_path: str
    p21_report_path: str
    working_rules_path: str
    test_case_path: str
    original_data_dir: str
    dirty_data_dir: str
    skipped_rules_path: str | None = None
