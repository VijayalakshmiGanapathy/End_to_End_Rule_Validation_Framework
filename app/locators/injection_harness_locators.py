from selenium.webdriver.common.by import By


class InjectionHarnessLocators:
    """
    Locators for the SDTM Error Injection Harness.
    """

    # -----------------------------
    # Upload Section
    # -----------------------------

    UPLOAD_RADIO_BUTTON = (
        By.XPATH,
        "//label[.//p[normalize-space()='Upload']]",
    )

    UPLOAD_BUTTON = (
        By.XPATH,
        "//button[.//p[normalize-space()='Upload']]",
    )

    FILE_UPLOAD_INPUT = (
        By.CSS_SELECTOR,
        "input[data-testid='stFileUploaderDropzoneInput']",
    )

    # ---------------------------------------------------------
    # Rule Search
    # ---------------------------------------------------------

    RULE_SEARCH_BOX = (
        By.CSS_SELECTOR,
        "input[placeholder='Rule ID or message…']",
    )

    SELECT_FILTERED_BUTTON = (
        By.XPATH,
        "//button[.//p[normalize-space()='Select filtered']]",
    )

    CLEAR_ALL_BUTTON = (
        By.XPATH,
        "//button[.//p[normalize-space()='Clear all']]",
    )

    RULE_CHECKBOX = (
        By.CSS_SELECTOR,
        "td[data-testid^='glide-cell-0-']",
    )

    RULE_GRID = (
        By.CLASS_NAME,
        "dvn-scroller",
    )

    
    

    RUN_INJECTION_BUTTON = (
        By.XPATH,
        "//button[.//p[normalize-space()='Run injection']]",
    )

    DOWNLOAD_MANIFEST_BUTTON = (
        By.XPATH,
        "//button[.//p[normalize-space()='Download manifest.json']]",
    )

    DOWNLOAD_IMPUTED_DATASET_CSV_BUTTON = (
        By.XPATH,
            "//button[.//p[contains(normalize-space(),'Download imputed dataset CSV')]]",
        )

    EXPORT_SUMMARY_TABLE = (
        By.XPATH,
        "//div[@data-testid='stDataFrame']",
    )

    DOWNLOAD_EXPORT_SUMMARY_BUTTON = (
        By.CSS_SELECTOR,
        "button[aria-label='Download as CSV']",
    )

    AUDIT_TABLE = (
        By.XPATH,
        "//div[@data-testid='stDataFrame']",
    )

    DOWNLOAD_AUDIT_REPORT_BUTTON = (
        By.CSS_SELECTOR,
        "button[aria-label='Download as CSV']",
    )

    # @staticmethod
    # def navigation_radio(page_name: str):
    #     return (
    #         By.XPATH,
    #         f"//label[@data-baseweb='radio'][.//p[normalize-space()='{page_name}']]",
    #     )
    

    # @staticmethod
    # def navigation_radio(page_name: str):
    #     return (
    #         By.XPATH,
    #         f"//p[normalize-space()='{page_name}']"
    #     )

   

    @staticmethod
    def navigation_radio(page_name):

        return [
            (
                By.XPATH,
                f"//label[@data-testid='stRadioOption'][.//p[normalize-space()='{page_name}']]"
            ),
            (
                By.XPATH,
                f"//label[.//p[normalize-space()='{page_name}']]"
            ),
            (
                By.XPATH,
                f"//*[normalize-space(text())='{page_name}']/ancestor::label[1]"
            ),
        ]
    
    AUDIT_RADIO_BUTTON = navigation_radio("Audit")

    @staticmethod
    def download_imputed_dataset_csv_button():

        return [

            (
                By.XPATH,
                "//button[.//p[contains(.,'Download imputed dataset')]]",
            ),

            (
                By.XPATH,
                "//button[.//p[contains(.,'dirty CSV')]]",
            ),

            (
                By.XPATH,
                "//div[@data-testid='stDownloadButton']//button",
            ),
        ]
    