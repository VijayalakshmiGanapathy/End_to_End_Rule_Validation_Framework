import logging
import os
import time
from pathlib import Path


from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.services.injection_download_service import (
    InjectionDownloadService,
)

from app.core.config import (
    INJECTION_HARNESS_URL,
    DEMO_MODE,
    DEMO_DELAY,
)
from app.locators.injection_harness_locators import (
    InjectionHarnessLocators,
)
from app.selenium.waits import Waits

import logging

from app.core.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

class InjectionHarnessService:
    """
    Automates the SDTM Error Injection Harness workflow.
    """

    def __init__(
        self,
        driver,
        batch_name: str,
    ):
        """
        Initialize the Injection Harness service.

        Args:
            driver: Selenium WebDriver instance.
            batch_name: Current batch being processed.
        """

        self.driver = driver
        self.batch_name = batch_name

    def pause(
        self,
        message: str = "",
    ):
        """
        Pause between automation steps when demo mode is enabled.
        """

        if message:
            print(message)

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | {message}"
            )

        if DEMO_MODE:
            time.sleep(DEMO_DELAY)

    def open_home_page(self):
        """
        Open the SDTM Error Injection Harness home page.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Opening SDTM Error Injection Harness."
            )

            self.driver.get(INJECTION_HARNESS_URL)

            self.driver.maximize_window()

            self.pause(
                "Opened SDTM Error Injection Harness."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to open SDTM Error Injection Harness."
            )

            raise

    def click_upload_radio_button(self):
        """
        Select the Upload radio button.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Selecting Upload option."
            )

            upload_radio = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.UPLOAD_RADIO_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                upload_radio,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                upload_radio,
            )

            self.pause(
                "Upload option selected."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to select Upload option."
            )

            raise

    def click_upload_button(self):
        """
        Click the Upload button.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Clicking Upload button."
            )

            upload_button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.UPLOAD_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                upload_button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                upload_button,
            )

            self.pause(
                "Upload button clicked."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to click Upload button."
            )

            raise

    def upload_original_data(
        self,
        original_data_folder: Path,
    ):
        """
        Upload all CSV files from the Original_data folder.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Uploading CSV files."
            )

            csv_files = sorted(
                original_data_folder.glob("*.csv")
            )

            if not csv_files:

                raise FileNotFoundError(
                    f"No CSV files found in: {original_data_folder}"
                )

            file_paths = "\n".join(
                str(file.resolve())
                for file in csv_files
            )

            upload_input = Waits.present(
                self.driver,
                InjectionHarnessLocators.FILE_UPLOAD_INPUT,
            )

            upload_input.send_keys(file_paths)

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Uploaded {len(csv_files)} CSV files."
            )

            self.pause(
                f"Uploaded {len(csv_files)} CSV files."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to upload CSV files."
            )

            raise

    
    def search_rule(
        self,
        rule_id: str,
    ):
        """
        Search a Rule ID.
        """

        search_box = Waits.visible(
            self.driver,
            InjectionHarnessLocators.RULE_SEARCH_BOX,
        )

        # Clear previous search
        search_box.send_keys(
            Keys.CONTROL,
            "a",
        )

        search_box.send_keys(
            Keys.DELETE,
        )

        # Enter Rule ID
        search_box.send_keys(rule_id)

        # Filter grid
        search_box.send_keys(Keys.ENTER)

        self.pause(
            f"Searched Rule: {rule_id}"
        )

    
    def click_select_filtered(self) -> bool:
        """
        Click the Select filtered button.

        Returns
        -------
        bool
            True if the button was clicked successfully,
            otherwise False.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Clicking Select filtered."
            )

            button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.SELECT_FILTERED_BUTTON,
                timeout=5,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                button,
            )

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Select filtered clicked."
            )

            self.pause(
                "Clicked Select filtered."
            )

            return True

        except Exception:

            logger.warning(
                f"Batch: {self.batch_name} | InjectionHarness | Select filtered button unavailable."
            )

            return False

    def select_rule(
        self,
        rule_id: str,
    ) -> bool:
        """
        Search and select a Rule ID.

        Parameters
        ----------
        rule_id : str
            Rule ID to select.

        Returns
        -------
        bool
            True if the rule was selected successfully,
            otherwise False.
        """

        try:

            # Search the Rule ID
            self.search_rule(rule_id)

            # Click Select filtered
            if not self.click_select_filtered():

                logger.warning(
                    f"Batch: {self.batch_name} | InjectionHarness | Rule '{rule_id}' not found."
                )

                return False

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Selected Rule: {rule_id}"
            )

            self.pause(
                f"Selected Rule: {rule_id}"
            )

            return True

        except Exception as ex:

            logger.warning(
                f"Batch: {self.batch_name} | InjectionHarness | "
                f"Rule '{rule_id}' could not be selected. "
                f"Error: {ex}"
            )

            return False
        
    def select_rules(
        self,
        rule_ids: list[str],
    ):
        """
        Select all Rule IDs for the current batch.

        Parameters
        ----------
        rule_ids : list[str]
            List of Rule IDs to select.
        """

        selected_count = 0
        missing_rules = []

        logger.info(
            f"Batch: {self.batch_name} | InjectionHarness | "
            f"Selecting {len(rule_ids)} rules."
        )

        for rule_id in rule_ids:

            if self.select_rule(rule_id):

                selected_count += 1

            else:

                missing_rules.append(rule_id)

        logger.info(
            f"Batch: {self.batch_name} | "
            f"Rule Selection Summary | "
            f"Selected: {selected_count} | "
            f"Missing: {len(missing_rules)}"
        )

        if missing_rules:

            logger.warning(
                f"Batch: {self.batch_name} | "
                f"Missing Rule IDs: {', '.join(missing_rules)}"
            )

        self.pause(
            f"Rule Selection Completed. "
            f"Selected: {selected_count}, "
            f"Missing: {len(missing_rules)}"
        )

    def click_run_radio_button(self):
        """
        Navigate to the Run page.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Opening Run page."
            )

            run_button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.navigation_radio("Run"),
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                run_button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                run_button,
            )

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Run page opened."
            )

            self.pause(
                "Opened Run page."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to open Run page."
            )

            raise

    def navigate_to_page(
        self,
        page_name: str,
    ):
        logger.info(
            f"Batch: {self.batch_name} | Navigating to {page_name} page."
        )

        radio = Waits.clickable(
            self.driver,
            InjectionHarnessLocators.navigation_radio(page_name),
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            radio,
        )

        self.driver.execute_script(
            "arguments[0].click();",
            radio,
        )

        self.pause(
            f"Navigated to {page_name} page."
        )

    def click_run_injection(self):
        """
        Click the Run Injection button.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Starting error injection."
            )

            run_button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.RUN_INJECTION_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                run_button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                run_button,
            )

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Error injection started."
            )

            
        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to click Run Injection."
            )

            raise

    def wait_for_results_page(self):
        """
        Wait until the Results page is loaded after injection.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | Waiting for error injection to complete."
            )

            Waits.visible(
                self.driver,
                InjectionHarnessLocators.DOWNLOAD_MANIFEST_BUTTON,
                timeout=300,
            )

            logger.info(
                f"Batch: {self.batch_name} | Results page loaded successfully."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | Results page did not load."
            )

            raise

    def download_manifest(self):
        """
        Download the manifest.json file from the Results page.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Downloading manifest.json."
            )

            button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.DOWNLOAD_MANIFEST_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                button,
            )

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Manifest download started."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to download manifest.json."
            )

            raise

    def download_dirty_csv(self):
        """
        Download the Dirty CSV ZIP file from the Results page.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Downloading Dirty CSV ZIP."
            )

            button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.DOWNLOAD_DIRTY_CSV_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                button,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                button,
            )

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Dirty CSV download started."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to download Dirty CSV."
            )

            raise


    def download_export_summary(self):
        """
        Download the Export Summary Excel file.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Downloading Export Summary."
            )

            # Hover over the dataframe
            table = Waits.visible(
                self.driver,
                InjectionHarnessLocators.EXPORT_SUMMARY_TABLE,
            )

            ActionChains(self.driver).move_to_element(table).perform()

            # Wait a moment for the toolbar to appear
            time.sleep(1)

            # Click the Download as CSV button
            button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.DOWNLOAD_EXPORT_SUMMARY_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                button,
            )

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Export Summary download started."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to download Export Summary."
            )

            raise

    def click_audit_page(self):
        """
        Navigate to the Audit page.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Opening Audit page."
            )

            button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.AUDIT_RADIO_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                button,
            )

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Audit page opened."
            )

            time.sleep(2)

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to open Audit page."
            )

            raise


    def download_audit_report(self):
        """
        Download Audit Report CSV.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Downloading Audit Report."
            )

            table = Waits.visible(
                self.driver,
                InjectionHarnessLocators.AUDIT_TABLE,
            )

            ActionChains(
                self.driver,
            ).move_to_element(
                table,
            ).perform()

            time.sleep(1)

            button = Waits.clickable(
                self.driver,
                InjectionHarnessLocators.DOWNLOAD_AUDIT_REPORT_BUTTON,
            )

            self.driver.execute_script(
                "arguments[0].click();",
                button,
            )

            logger.info(
                f"Batch: {self.batch_name} | InjectionHarness | Audit Report download started."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | InjectionHarness | Failed to download Audit Report."
            )

            raise

    def run(
        self,
        original_data_folder: Path,
        rule_ids: list[str],
        temp_folder: Path,
        batch_folder: Path,
    ):
        """
        Execute the complete SDTM Error Injection Harness workflow.

        Args:
            original_data_folder: Path to the Original_data folder.
            rule_ids: List of Rule IDs to inject.
        """

        try:

            logger.info(
                f"Batch: {self.batch_name} | Injection Harness workflow started."
            )

            # Step 1 Open Injection Harness
            self.open_home_page()

            # Step 2 Select Upload Option
            self.click_upload_radio_button()

            # Step 3 Upload Original Data
            self.upload_original_data(
                original_data_folder,
            )

            # Step 4 Select Rule IDs
            self.select_rules(
                rule_ids,
            )

            self.navigate_to_page("Run")

            self.click_run_injection()

            self.wait_for_results_page()

            download_service = InjectionDownloadService()   

            self.download_manifest()

            download_service.process_manifest(
                temp_folder,
                batch_folder,
                self.batch_name,
            )

            self.download_dirty_csv()

            download_service.process_dirty_csv(
                temp_folder,
                batch_folder,
                self.batch_name,
            )

            # Delete old export files
            for file in temp_folder.glob("*_export.csv"):
                logger.info(f"Deleting old file: {file.name}")
                file.unlink()
            # ---------------------------------------
            # Download Export Summary
            # ---------------------------------------

            self.download_export_summary()

            download_service.process_export_summary(
                temp_folder,
                batch_folder,
                self.batch_name,
            )
            
           # ---------------------------------------
            # Audit Report
            # ---------------------------------------

            self.click_audit_page()

            # Delete old export files
            for file in temp_folder.glob("*_export.csv"):
                logger.info(f"Deleting old export file: {file.name}")
                file.unlink()

            self.download_audit_report()

            download_service.process_audit_report(
                temp_folder,
                batch_folder,
                self.batch_name,
            )

            logger.info(
                f"Batch: {self.batch_name} | Injection Harness workflow completed successfully."
            )

        except Exception:

            logger.exception(
                f"Batch: {self.batch_name} | Injection Harness workflow failed."
            )

            raise    