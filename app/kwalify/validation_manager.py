"""
Validation manager.
"""

import time

from app.kwalify.constants import VALIDATION_BASE_URL

from app.core.timer import StepTimer
from app.core.log_helper import info, success, warning, error

import logging

logger = logging.getLogger(__name__)


class ValidationManager:

    def __init__(self, client):
        self.client = client

    def convert(self, study_name):

        response = self.client.post(
            f"{VALIDATION_BASE_URL}/validation/convert/",
            params={
                "study_id": study_name,
            },
        )

        return response.json()

    def validate(self, study_name):

        response = self.client.post(
            f"{VALIDATION_BASE_URL}/validation/validate/",
            params={
                "study_id": study_name,
            },
        )

        return response.json()

    def consolidate(self, study_name, run_id):

        response = self.client.post(
            f"{VALIDATION_BASE_URL}/validation/consolidate/",
            params={
                "study_id": study_name,
                "run_id": run_id,
            },
        )

        return response.json()

    def run_validation(self, study_name):

        total_timer = StepTimer()
        total_timer.start()

        # ---------------- Conversion ----------------

        timer = StepTimer()
        timer.start()

        logger.info("Converting study...")

        print("Calling Convert API")

        conversion = self.convert(study_name)

        success(
            f"Conversion completed ({timer.stop():.2f}s)"
        )

        print("Convert Finished")

        print(conversion)


        # # ---------------- Wait ----------------

        # info("Waiting for conversion to complete...")
        # time.sleep(10)

        # ---------------- Validation ----------------

        timer = StepTimer()
        timer.start()

        info("Running validation...")

        logger.info("Calling Validation API...")

        

        validation = self.validate(study_name)

        

        success(
            f"Validation completed ({timer.stop():.2f}s)"
        )

        run_id = validation["run_id"]

        info(f"Run ID : {run_id}")

        # ---------------- Consolidation ----------------

        timer = StepTimer()
        timer.start()

        info("Consolidating results...")

        self.consolidate(
            study_name,
            run_id,
        )

        success(
            f"Consolidation completed ({timer.stop():.2f}s)"
        )

        

        # Wait for frontend/database to update
        info("Waiting 30 seconds for frontend to update validation status...")
        time.sleep(30)
        success("Wait completed.")

        success(
            f"Validation workflow completed ({total_timer.stop():.2f}s)"
        )
        
        return run_id
    
    logger.info("Validation API returned successfully.")