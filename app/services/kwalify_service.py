import logging

from app.kwalify.api_client import APIClient
from app.kwalify.auth_manager import AuthManager
from app.kwalify.study_manager import StudyManager
from app.kwalify.upload_manager import UploadManager
from app.kwalify.validation_manager import ValidationManager

logger = logging.getLogger(__name__)


class KwalifyService:

    def __init__(self):

        self.client = APIClient()

        self.auth = AuthManager(self.client)

        self.study = StudyManager(self.client)

        self.upload = UploadManager(self.client)

        self.validation = ValidationManager(self.client)

    def run(
        self,
        paths,
        config,
        run_number,
    ):

        logger.info("========== Kwalify ==========")

        # Login
        self.auth.login()
        logger.info("Login successful.")

        study_name = config.batch_name

        # Create Study
        if not self.study.study_exists(study_name):

            logger.info(f"Creating study : {study_name}")

            self.study.create_study(study_name)

        else:

            logger.info(f"Study already exists : {study_name}")

        # Configure Domains
        domains = self.study.get_batch_domains(paths)

        self.study.save_domains(
            study_name,
            domains,
        )

        logger.info("Domains configured.")

        # Upload Dirty CSV
        self.upload.upload_batch(
            study_name,
            paths,
        )

        logger.info("Upload completed.")

        # Validation
        run_id = self.validation.run_validation(
            study_name,
        )

        logger.info(f"Run ID : {run_id}")

        return run_id