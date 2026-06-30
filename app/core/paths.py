from pathlib import Path

from app.core.config import DATA_DIR

from app.core.constants import (
    ORIGINAL_DATA_FOLDER,
    DIRTY_FOLDER,
    TEMP_FOLDER,
    P21_REPORT_FOLDER,
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