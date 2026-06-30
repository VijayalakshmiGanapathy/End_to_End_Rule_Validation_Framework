from pathlib import Path
import time
from app.locators.trialgen_locators import TrialGenLocators

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.selenium.waits import Waits

from app.core.config import (
    TRIALGEN_HOME_URL,
    TRIALGEN_SUBJECT_COUNT,
    TRIALGEN_RANDOM_SEED,
    DEMO_MODE, 
    DEMO_DELAY,
)

import logging

from app.core.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

class TrialGenService:
    """
    Automates TrialGen dataset generation.
    """

    BASE_URL = TRIALGEN_HOME_URL

    SUBJECT_COUNT = TRIALGEN_SUBJECT_COUNT

    def __init__(self, driver, batch_name: str):

        self.driver = driver
        self.batch_name = batch_name

    def open(self):

        self.driver.get(self.BASE_URL)

    def pause(self, message: str = ""):
        """
        Display and log the current automation step.
        """

        if message:
            print(message)

            logger.info(
                f"Batch: {self.batch_name} | TrialGen | {message}"
            )

        if DEMO_MODE:
            time.sleep(DEMO_DELAY)


    def open_home_page(self):
        """
        Open TrialGen home page.
        """

        try:
            self.driver.get(TRIALGEN_HOME_URL)

            self.driver.maximize_window()

            self.pause("Opened TrialGen Home Page")

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | Failed to open home page."
            )

            raise
    
    
    def click_clinical_study(self):
        """
        Navigate to the Clinical Study Data generation page.
        """

        try:
            logger.info(
                f"Batch: {self.batch_name} | TrialGen | Opening Clinical Study Data page."
            )

            clinical_card = WebDriverWait(
                self.driver,
                30,
            ).until(
                EC.element_to_be_clickable(
                    TrialGenLocators.CLINICAL_STUDY_CARD
                )
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                clinical_card,
            )

            clinical_card.click()

            WebDriverWait(
                self.driver,
                30,
            ).until(
                EC.url_contains("/generate/sdtm")
            )

            self.pause("Clinical Study Data page opened.")

        except Exception:
            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | Failed to open Clinical Study Data page."
            )
            raise

    def search_protocol(
        self,
        protocol: str,
    ):
        """
        Search the protocol using the Host Generator Key.
        """

        try:
            logger.info(
                f"Batch: {self.batch_name} | TrialGen | Searching protocol: {protocol}"
            )

            search_box = WebDriverWait(
                self.driver,
                20,
            ).until(
                EC.visibility_of_element_located(
                    TrialGenLocators.SEARCH_BOX
                )
            )

            search_box.click()

            search_box.send_keys(
                Keys.CONTROL,
                "a",
            )

            search_box.send_keys(
                Keys.DELETE,
            )

            search_box.send_keys(protocol)

            self.pause(f"Protocol searched: {protocol}")

        except Exception:
            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | Failed to search protocol: {protocol}"
            )
            raise

    def select_protocol(
        self,
        protocol: str,
    ):
        """
        Select the protocol from the filtered protocol list.
        """

        try:
            logger.info(
                f"Batch: {self.batch_name} | TrialGen | Selecting protocol: {protocol}"
            )

            protocol_row = WebDriverWait(
                self.driver,
                20,
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//span[contains(text(),'{protocol}')]",
                    )
                )
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                protocol_row,
            )

            protocol_row.click()

            self.pause(f"Protocol selected: {protocol}")

        except Exception:
            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | Failed to select protocol: {protocol}"
            )
            raise

    def enter_subject_count(self):
        """
        Set the configured subject count using JavaScript.
        """

        try:
            logger.info(
                f"Batch: {self.batch_name} | TrialGen | Updating subject count."
            )

            subject_box = Waits.visible(
                self.driver,
                TrialGenLocators.SUBJECT_COUNT,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                subject_box,
            )

            self.driver.execute_script(
                "arguments[0].focus();",
                subject_box,
            )

            self.driver.execute_script(
                """
                const input = arguments[0];
                const value = arguments[1];

                const nativeInputValueSetter =
                    Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype,
                        'value'
                    ).set;

                nativeInputValueSetter.call(input, value);

                input.dispatchEvent(
                    new Event('input', { bubbles: true })
                );

                input.dispatchEvent(
                    new Event('change', { bubbles: true })
                );
                """,
                subject_box,
                self.SUBJECT_COUNT,
            )

            current_value = self.driver.execute_script(
                "return arguments[0].value;",
                subject_box,
            )

            self.pause(
                f"Subject count updated to {current_value}."
            )

        except Exception:
            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | Failed to update subject count."
            )
            raise

    def click_generate(self):
        """
        Click the Generate Dataset button.
        """

        try:
            logger.info(
                f"Batch: {self.batch_name} | TrialGen | Generating dataset."
            )

            generate_button = Waits.clickable(
                self.driver,
                TrialGenLocators.GENERATE_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
            generate_button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                generate_button,
            )

            self.pause("Generate Dataset button clicked.")

        except Exception:
            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | Failed to click Generate Dataset."
            )
            raise

    

    def click_view_results(self):
        """
        Open the TrialGen results page.
        """

        try:
            logger.info(
                f"Batch: {self.batch_name} | TrialGen | Opening results page."
            )

            view_button = Waits.clickable(
                self.driver,
                TrialGenLocators.VIEW_RESULTS_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                view_button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                view_button,
            )

            self.pause("View Results page opened.")

        except Exception:
            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | Failed to open results page."
            )
            raise

    def click_download_complete_dataset(self):
        """
        Download the generated TrialGen dataset.
        """

        try:
            logger.info(
                f"Batch: {self.batch_name} | TrialGen | Starting dataset download."
            )

            download_button = Waits.clickable(
                self.driver,
                TrialGenLocators.DOWNLOAD_COMPLETE_DATASET_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                download_button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                download_button,
            )

            self.pause("Dataset download started.")

        except Exception:
            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | Failed to download dataset."
            )
            raise

    def run(
        self,
        host_generator_key: str,
    ):
        """
        Execute the complete TrialGen automation workflow.

        Steps:
            1. Open TrialGen home page.
            2. Navigate to Clinical Study Data page.
            3. Search and select the protocol.
            4. Set the subject count.
            5. Generate the dataset.
            6. Open the Results page.
            7. Download the generated dataset.
        """

        try:
            logger.info(
                f"Batch: {self.batch_name} | TrialGen | TrialGen automation started."
            )

            self.open_home_page()

            self.click_clinical_study()

            self.search_protocol(
                host_generator_key,
            )

            self.select_protocol(
                host_generator_key,
            )

            self.enter_subject_count()

            self.click_generate()

            self.click_view_results()

            self.click_download_complete_dataset()

            logger.info(
                f"Batch: {self.batch_name} | TrialGen | TrialGen automation completed successfully."
            )

        except Exception:
            logger.exception(
                f"Batch: {self.batch_name} | TrialGen | TrialGen automation failed."
            )
            raise