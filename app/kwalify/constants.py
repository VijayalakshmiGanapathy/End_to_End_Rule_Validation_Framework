# ==========================
# Study Defaults
# ==========================

SPONSOR = "BioMedical"

EXPECTED_SUBJECT_COUNT = 50

SDTM_VERSION = "3.4"

SDTM_VERSION_ID = 1

STUDY_DESCRIPTION_SUFFIX = "kwalify validation (Automated)."

CREATED_BY = "Automation"

# ==========================
# API URLs
# ==========================

AUTH_BASE_URL = "http://103.189.89.49:8003/admin"

STUDY_BASE_URL = "http://103.189.89.49:8000"

VALIDATION_BASE_URL = "http://103.189.89.49:8001"

# ==========================
# API Endpoints
# ==========================

LOGIN_ENDPOINT = "/auth/login"

STUDIES_ENDPOINT = "/study/studies"

DOMAINS_ENDPOINT = "/study/sdtm/versions/1/domains"

SAVE_DOMAINS_ENDPOINT = "/study/studies/{study_id}/domains"

CONVERT_ENDPOINT = "/validation/convert/"

VALIDATE_ENDPOINT = "/validation/validate/"

CONSOLIDATE_ENDPOINT = "/validation/consolidate/"