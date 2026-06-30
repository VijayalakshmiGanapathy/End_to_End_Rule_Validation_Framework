from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Waits:

    @staticmethod
    def visible(driver, locator, timeout=30):

        return WebDriverWait(
            driver,
            timeout,
        ).until(
            EC.visibility_of_element_located(locator)
        )

    @staticmethod
    def clickable(driver, locator, timeout=30):

        return WebDriverWait(
            driver,
            timeout,
        ).until(
            EC.element_to_be_clickable(locator)
        )
    
    @staticmethod
    def present(
        driver,
        locator,
        timeout=30,
    ):
        """
        Wait until an element is present in the DOM.
        Useful for hidden file input elements.
        """

        return WebDriverWait(
            driver,
            timeout,
        ).until(
            EC.presence_of_element_located(locator)
        )