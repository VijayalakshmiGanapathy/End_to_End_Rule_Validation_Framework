from app.selenium.download_manager import DownloadManager
from app.selenium.selenium_driver import SeleniumDriver


def test_driver():

    folder = DownloadManager.get_batch_download_folder(
        "B01_DM_dates"
    )

    driver = SeleniumDriver(folder).get_driver()

    driver.get("https://trialgen.care2data.com/")

    input("Press Enter to close browser...")

    driver.quit()


if __name__ == "__main__":

    test_driver()