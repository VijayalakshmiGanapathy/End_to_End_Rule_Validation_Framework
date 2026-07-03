from pathlib import Path

from app.core.config import DATA_DIR

from app.core.constants import (
    ORIGINAL_DATA_FOLDER,
    DIRTY_FOLDER,
    TEMP_FOLDER,
    P21_REPORT_FOLDER,
    TEST_VALIDATION_REPORT_FOLDER,
    KWALIFY_REPORT_FOLDER,
    COMPARISON_REPORT_FOLDER,
)


class BatchPaths:

    def __init__(
        self,
        batch_name: str,
    ):

        self.batch_name = batch_name

        self.batch_folder = (
            DATA_DIR /
            "batches" /
            batch_name
        )

        self.original_data = (
            self.batch_folder /
            ORIGINAL_DATA_FOLDER
        )

        self.temp = (
            self.batch_folder /
            TEMP_FOLDER
        )

        self.dirty = (
            self.batch_folder /
            DIRTY_FOLDER
        )

        self.p21_reports = (
            self.batch_folder /
            P21_REPORT_FOLDER
        )

       
       

        self.comparison_reports = (
            self.batch_folder /
            COMPARISON_REPORT_FOLDER
        )

    @property
    def batch_prefix(self):

        return self.batch_name[:3]

    def create(self):

        self.batch_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.temp.mkdir(
            exist_ok=True,
        )

        self.p21_reports.mkdir(
            exist_ok=True,
        )

        self.test_validation_report_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.kwalify_reports.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.comparison_reports.mkdir(
            parents=True,
            exist_ok=True,
        )

    @property
    def export_summary(self):

        return (
            self.batch_folder /
            f"export_summary_{self.batch_prefix}.csv"
        )


    @property
    def audit_report(self):

        return (
            self.batch_folder /
            f"export_audit_report_{self.batch_prefix}.csv"
        )

    @property
    def test_validation_report_folder(self):

        folder = (
            self.batch_folder /
            "Test_Validation_Report"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder
    
    @property
    def test_validation_report(self):

        return (
            self.test_validation_report_folder /
            f"Test_Validation_Report_{self.batch_prefix}.xlsx"
        )

    @property
    def kwalify_reports(self):
        folder = self.batch_folder / "Kwalify_reports"
        folder.mkdir(
            parents=True,
            exist_ok=True,
        )
        return folder
    
    @property
    def latest_kwalify_report(self):
        return self.kwalify_reports / f"Kwalify_{self.batch_prefix}.xlsx"
    

    @property
    def latest_p21_report(self):

        pass