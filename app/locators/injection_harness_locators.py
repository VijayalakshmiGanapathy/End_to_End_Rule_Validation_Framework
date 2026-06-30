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

    SELECT_FILTERED_BUTTON = (
        By.XPATH,
        "//button[.//p[text()='Select filtered']]",
    )

    

    RUN_INJECTION_BUTTON = (
        By.XPATH,
        "//button[.//p[normalize-space()='Run injection']]",
    )

    DOWNLOAD_MANIFEST_BUTTON = (
        By.XPATH,
        "//button[.//p[normalize-space()='Download manifest.json']]",
    )

    DOWNLOAD_DIRTY_CSV_BUTTON = (
        By.XPATH,
        "//button[.//p[normalize-space()='Download dirty CSVs']]",
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

    @staticmethod
    def navigation_radio(page_name: str):
        return (
            By.XPATH,
            f"//label[@data-baseweb='radio'][.//p[normalize-space()='{page_name}']]",
        )
    
    AUDIT_RADIO_BUTTON = navigation_radio("Audit")
    