import shutil
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from app.kwalify.config import (
    FRONTEND_URL,
    FRONTEND_USERNAME,
    FRONTEND_PASSWORD,
)


from app.core.timer import StepTimer
from app.core.log_helper import info, success, warning, error

import logging

logger = logging.getLogger(__name__)

class ReportDownloader:

    def __init__(self):

        options = Options()

        options.add_argument(
            r"--user-data-dir=D:\Test Automation\Kwalify_Run_Auto\chrome_profile"
        )

        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")

        prefs = {
            "download.default_directory": r"D:\Test Automation\Kwalify_Run_Auto\downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }

        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

        self.wait = WebDriverWait(self.driver, 20)

    def login(self, batch_name, run_id):

        total_timer = StepTimer()
        total_timer.start()

        self.driver.get(FRONTEND_URL)

        time.sleep(3)

        if "/dashboard" not in self.driver.current_url:

            info("Logging into frontend...")

            self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//input[@formcontrolname='username']")
                )
            ).send_keys(FRONTEND_USERNAME)

            self.driver.find_element(
                By.XPATH,
                "//input[@formcontrolname='password']"
            ).send_keys(FRONTEND_PASSWORD)

            self.driver.find_element(
                By.XPATH,
                "//button[@type='submit']"
            ).click()

            self.wait.until(
                EC.url_contains("/dashboard")
            )

        success("Frontend login successful")

        info(f"Opening study '{batch_name}'...")

        self.driver.get(f"{FRONTEND_URL}/admin/dashboard")

        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//table")
            )
        )

        study_row = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//tr[.//h6[normalize-space()='{batch_name}']]"
                )
            )
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            study_row,
        )

        time.sleep(1)

        study_row.click()

        self.wait.until(
            EC.url_contains("study-management?id=")
        )

        success(f"Opened study: {batch_name}")

        download_folder = Path(
            r"D:\Test Automation\Kwalify_Run_Auto\downloads"
        )

        download_folder.mkdir(
            exist_ok=True
        )

        for file in download_folder.glob(
            "Validation_Report_*.xlsx"
        ):
            try:
                file.unlink()
            except Exception:
                pass

        info(f"Downloading report for {run_id}...")

        row = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//tr[td[contains(normalize-space(), '{run_id}')]]"
                )
            )
        )

        download_button = row.find_element(
            By.XPATH,
            ".//button[.//mat-icon[text()='save_alt']]"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            download_button,
        )

        time.sleep(1)

        download_button.click()

        success(f"Clicked download for {run_id}")

        latest_file = None

        for _ in range(60):

            files = list(
                download_folder.glob(
                    "Validation_Report_*.xlsx"
                )
            )

            if files:

                latest_file = max(
                    files,
                    key=lambda x: x.stat().st_mtime,
                )

                if not latest_file.name.endswith(
                    ".crdownload"
                ):
                    break

            time.sleep(1)

        if latest_file is None:

            self.driver.quit()

            raise RuntimeError(
                "Validation report download failed."
            )

        success(f"Downloaded {latest_file.name}")

        report_folder = (
            Path(r"D:\Test Automation\Data\Batches")
            / batch_name
            / "Kwalify Report"
        )

        report_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            report_folder /
            f"K_{batch_name[:3]}_{run_id}.xlsx"
        )

        shutil.move(
            str(latest_file),
            str(destination),
        )

        success(f"Saved report to {destination}")

        success(
            f"Report workflow completed ({total_timer.stop():.2f}s)"
        )

        self.driver.quit()