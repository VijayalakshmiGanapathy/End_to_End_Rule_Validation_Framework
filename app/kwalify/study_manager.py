"""
Study manager.

Responsible for determining which batch folders need to be processed.
"""



from app.kwalify.constants import (
    STUDY_BASE_URL,
    STUDIES_ENDPOINT,
    SPONSOR,
    EXPECTED_SUBJECT_COUNT,
    SDTM_VERSION,
    SDTM_VERSION_ID,
    STUDY_DESCRIPTION_SUFFIX,
    CREATED_BY,
    DOMAINS_ENDPOINT,
)


from app.core.timer import StepTimer
from app.core.log_helper import info, success, warning, error

import logging

logger = logging.getLogger(__name__)

class StudyManager:

    def __init__(self, client):
        self.client = client

    # def __init__(self, client):
    #     self.client = client
    #     self.batch_folder = BATCHES_FOLDER

    # def get_batches(self):
    #     """
    #     Return a list of batch folders to process.
    #     """

    #     if not self.batch_folder.exists():
    #         raise FileNotFoundError(
    #             f"Batch folder not found:\n{self.batch_folder}"
    #         )

    #     if RUN_MODE.lower() == "single":

    #         batch = self.batch_folder / SINGLE_BATCH

    #         if not batch.exists():
    #             raise FileNotFoundError(
    #                 f"Batch '{SINGLE_BATCH}' not found."
    #             )

    #         return [batch]

    #     return sorted(
    #         folder
    #         for folder in self.batch_folder.iterdir()
    #         if folder.is_dir()
    #     )

    def get_existing_studies(self):
        """
        Retrieve all existing study IDs.
        """

        response = self.client.get(
            f"{STUDY_BASE_URL}{STUDIES_ENDPOINT}"
        )

        data = response.json()

        return {
            study["study_id"]
            for study in data["resp"]
        }

    def study_exists(self, study_name):
        """
        Check whether a study already exists.
        """

        return study_name in self.get_existing_studies()

    def create_study(self, batch_name):
        """
        Create a new study.
        """

        timer = StepTimer()
        timer.start()

        payload = {
            "study_id": batch_name,
            "protocol_number": batch_name[:3],
            "study_title": batch_name,
            "phase": "",
            "therapeutic_area": "",
            "principle_investigator": "",
            "expected_subject_count": EXPECTED_SUBJECT_COUNT,
            "study_description": (
                f"{batch_name} {STUDY_DESCRIPTION_SUFFIX}"
            ),
            "sdtm_version": SDTM_VERSION,
            "sdtm_version_id": SDTM_VERSION_ID,
            "ct_version": "",
            "status": "Active",
            "sponsor": SPONSOR,
            "created_by": CREATED_BY,
        }

        response = self.client.post(
            f"{STUDY_BASE_URL}{STUDIES_ENDPOINT}",
            json=payload,
        )

        success(
            f"Study created ({timer.stop():.2f}s)"
        )

        return response.json()

    def get_batch_domains(self, paths):
        """
        Read all CSV files and determine required SDTM domains.
        """

        dirty_folder = paths.dirty

        domains = set()

        for file in dirty_folder.glob("*.csv"):

            filename = file.stem.upper()

            if filename.startswith("SUPP"):
                domains.add("SUPPQUAL")
            else:
                domains.add(filename[:2])

        info(f"Domains detected: {', '.join(sorted(domains))}")

        return sorted(domains)

    def get_domain_mapping(self):
        """
        Get SDTM domain IDs.
        """

        response = self.client.get(
            f"{STUDY_BASE_URL}{DOMAINS_ENDPOINT}"
        )

        data = response.json()

        mapping = {}

        for domain in data["resp"]["domains"]:
            mapping[
                domain["domain_code"]
            ] = domain["domain_def_id"]

        return mapping

    def save_domains(self, study_name, domains):
        """
        Save selected domains to study.
        """

        timer = StepTimer()
        timer.start()

        mapping = self.get_domain_mapping()

        domain_ids = []

        for domain in domains:
            if domain in mapping:
                domain_ids.append(
                    mapping[domain]
                )

        payload = {
            "domain_def_ids": domain_ids,
            "created_by": CREATED_BY,
        }

        response = self.client.post(
            f"{STUDY_BASE_URL}/study/studies/{study_name}/domains",
            json=payload,
        )

        success(
            f"{len(domain_ids)} domains configured ({timer.stop():.2f}s)"
        )

        return response.json()