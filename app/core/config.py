import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Return project base directory.

    Development:
        E:/Care2Data/rule_injection_validation_framework

    EXE:
        Folder where RuleValidationApp.exe is placed
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


BASE_DIR = get_base_dir()

DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_OUTPUT_FILE = OUTPUT_DIR / "rule_injection_validation_report.xlsx"

WORKING_RULES_FILE = INPUT_DIR / "Error_Injector_Working_Rule_Batches.xlsx"
TEST_CASE_FILE = INPUT_DIR / "SDTMIG Rule Test Case 1.xlsx"

WORKING_RULES_SHEET = "Batches"
ISSUE_SUMMARY_SHEET = "Issue Summary"
P21_RULES_SHEET = "Rules"

STUDY_SHEET = "Study"
RULE_SHEET = "Rule"
TEST_CASE_SHEET = "Test Case"

ROW_INDEX_OFFSET = 2
IMPUTATION_MATCH_THRESHOLD = 80.0

SDTM_DOMAINS = {
    "DM", "AE", "DS", "DV", "MH", "EX", "EC", "CM",
    "LB", "VS", "QS", "EG", "IE", "SE", "SV", "TS",
    "TA", "TE", "TI", "TV", "RELREC", "SUPPDM",
}

INPUT_DIR = Path("data/input")

WORKING_RULES_FILE = (
    INPUT_DIR
    / "SDTM_P21_Working_Rules_and_15_Batches 1.xlsx"
)

# TrialGen Configuration
TRIALGEN_SUBJECT_COUNT = 50
TRIALGEN_URL = "http://103.189.89.119:8081/"
TRIALGEN_GENERATE_URL = "http://103.189.89.119:8081//generate/sdtm"

# TrialGen

TRIALGEN_HOME_URL = "http://103.189.89.119:8081/"



TRIALGEN_RANDOM_SEED = 1

# Demo Settings

DEMO_MODE = False

DEMO_DELAY = 2  # seconds

# --------------------------------------------------
# SDTM Error Injection Harness
# --------------------------------------------------

INJECTION_HARNESS_URL = "http://103.189.89.119:8089/"



# Folder Names
ORIGINAL_DATA_FOLDER = "Original_data"
DIRTY_FOLDER = "dirty"
TEMP_FOLDER = "temp"
P21_REPORT_FOLDER = "P21_reports"

# Downloaded File Names
MANIFEST_FILE = "manifest"
DIRTY_ZIP_FILE = "dirty_csv"
EXPORT_SUMMARY_FILE = "export_summary"
EXPORT_AUDIT_REPORT_FILE = "export_audit_report"

# Extensions
JSON_EXTENSION = ".json"
ZIP_EXTENSION = ".zip"
EXCEL_EXTENSION = ".xlsx"