"""
Upload manager.
"""

import csv

from app.kwalify.constants import STUDY_BASE_URL

from app.core.timer import StepTimer
from app.core.log_helper import info, success, warning, error

import logging

logger = logging.getLogger(__name__)

class UploadManager:

    def __init__(self, client):
        self.client = client

    def upload_file(self, study_name, file_path):
        """
        Upload a single CSV file.
        """

        domain = file_path.stem.upper()

        if domain.startswith("SUPP"):
            domain = "SUPPQUAL"
        else:
            domain = domain[:2]

        with open(file_path, "rb") as f:

            files = {
                "file": (
                    file_path.name,
                    f,
                    "text/csv",
                )
            }

            response = self.client.post(
                f"{STUDY_BASE_URL}/study/studies/{study_name}/files/upload",
                params={
                    "domain": domain,
                    "overwrite": False,
                    "retain_versions": True,
                },
                files=files,
            )

        return response.json()

    def get_record_count(self, file_path):
        """
        Returns number of records excluding header.
        """

        with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
            return sum(1 for _ in csv.reader(csvfile)) - 1

    def upload_batch(self, study_name, paths):
        """
        Upload every CSV inside the dirty folder.
        """

        dirty_folder = paths.dirty

        total_timer = StepTimer()
        total_timer.start()

        uploaded = 0
        skipped = 0

        for file in sorted(dirty_folder.glob("*.csv")):

            timer = StepTimer()
            timer.start()

            records = self.get_record_count(file)

            info(f"Uploading {file.name} ({records} records)")

            response = self.upload_file(
                study_name,
                file,
            )

            elapsed = timer.stop()

            if response.get("status") == "exists":

                skipped += 1

                warning(
                    f"{file.name} already exists ({elapsed:.2f}s)"
                )

            else:

                uploaded += 1

                success(
                    f"{file.name} uploaded ({records} records, {elapsed:.2f}s)"
                )

        success(
            f"Upload complete | Uploaded: {uploaded} | Skipped: {skipped} | Time: {total_timer.stop():.2f}s"
        )