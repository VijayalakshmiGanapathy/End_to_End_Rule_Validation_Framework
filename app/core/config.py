from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "data" / "output"

DEFAULT_OUTPUT_FILE = OUTPUT_DIR / "rule_injection_validation_report.xlsx"

WORKING_RULES_SHEET = "15 Batches"
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