from selenium.webdriver.common.by import By


class TrialGenLocators:

    # ---------------- Home Page ---------------- #

    CLINICAL_STUDY_CARD = (
        By.XPATH,
        "//div[contains(@class,'type-card') and .//h2[text()='Clinical Study Data']]",
    )

    # ---------------- Generate Page ---------------- #

    SEARCH_BOX = (
        By.XPATH,
        "//app-protocol-selector//input",
    )

    SUBJECT_COUNT = (
        By.ID,
        "mat-input-1",
    )

    GENERATE_BUTTON = (
        By.XPATH,
        "//button[.//span[contains(normalize-space(),'Generate Dataset')]]",
    )

    DOWNLOAD_BUTTON = (
        By.XPATH,
        "//button[contains(.,'Download')]",
    )

    # ==========================
    # Result Page
    # ==========================

    VIEW_RESULTS_BUTTON = (
        By.XPATH,
        "//button[.//span[contains(normalize-space(),'View Results')]]",
    )

    DOWNLOAD_COMPLETE_DATASET_BUTTON = (
        By.XPATH,
        "//button[contains(@class,'download-all-btn')]",
    )