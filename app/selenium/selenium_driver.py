from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumDriver:
    """
    Creates reusable Chrome Driver.
    """

    def __init__(
        self,
        download_directory: Path,
        headless: bool = False,
    ):

        self.download_directory = Path(download_directory)

        self.headless = headless

    def get_driver(self):

        options = Options()

        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")

        options.add_argument("--disable-notifications")

        options.add_argument("--disable-popup-blocking")

        options.add_argument("--disable-infobars")

        options.add_argument("--allow-running-insecure-content")

        options.add_argument("--disable-popup-blocking")

        options.add_argument("--ignore-certificate-errors")

        prefs = {
            "download.default_directory": str(self.download_directory.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.extensions_to_open": "",

            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1,

            # Allow unsafe downloads
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
        }

        options.add_experimental_option(
            "prefs",
            prefs,
        )

        print("=" * 80)
        print("DOWNLOAD DIRECTORY")
        print(self.download_directory.resolve())
        print("=" * 80)

        driver = webdriver.Chrome(

            service=Service(
                ChromeDriverManager().install()
            ),

            options=options,
        )

        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": str(self.download_directory.resolve()),
            },
        )

        print(
            "Download Directory:",
            self.download_directory.resolve(),
        )


        driver.implicitly_wait(10)

        return driver