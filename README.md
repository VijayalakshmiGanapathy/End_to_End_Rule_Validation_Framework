# Automated Rule Injection Verification and Cross-Report Validation Framework

Python + FastAPI framework to validate whether SDTMIG rule injections in synthetic data are correctly imputed in Dirty CSV datasets and detected in Pinnacle 21 reports.

## Current Batch

```text
B01_DM_dates
```

## Objective

This project validates the complete rule injection flow for the **B01_DM_dates** batch.

It verifies:

* Rule IDs injected by the SDTM Error Injection Harness.
* Error imputation in Dirty CSV files by comparing Original vs Dirty datasets.
* Rule ID and Domain presence in Pinnacle 21 Issue Summary.
* Rule ID availability in Pinnacle 21 Rules sheet.
* Rule ID availability in SDTMIG Rule Test Case documentation.
* Final validation status and batch-level summary report.

## Features

* Batch-wise validation using Batch Name and Host Generator Key.
* Export Summary validation.
* Export Audit Report validation.
* Original vs Dirty CSV imputation comparison.
* Supports normal value changes, blank/null injections, invalid value injections, date changes, and duplicate row validation.
* P21 Issue Summary validation.
* P21 Rules sheet validation.
* SDTMIG Rule Test Case workbook checks.
* Rule ID + Domain validation between Export Audit Report and P21 Issue Summary.
* Excel report generation with batch-specific sheet names.
* Logging and exception handling.
* FastAPI endpoint for validation execution.

## Project Structure

```text
rule_injection_validation_framework/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── exceptions/
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── data/
│   ├── input/
│   │   ├── B01_DM_dates/
│   │   │   ├── Original_data/
│   │   │   ├── dirty/
│   │   │   ├── 2026-06-09T06-45_export.csv
│   │   │   ├── 2026-06-09T06-46_export.csv
│   │   │   ├── manifest.json
│   │   │   └── pinnacle21-report-2026-06-10T12-54-54-618.xlsx
│   │   │
│   │   ├── SDTM_P21_Working_Rules_and_15_Batches 1.xlsx
│   │   └── SDTMIG Rule Test Case 1.xlsx
│   │
│   └── output/
│
├── logs/
├── tests/
├── requirements.txt
└── README.md
```

## Input Files

### 1. Export Summary File

Used to identify injected Rule IDs.

Example:

```text
2026-06-09T06-46_export.csv
```

Expected columns:

```text
rule_id
injected
overwritten
failed_self_validation
total
failure_reason
```

### 2. Export Audit Report / Export Detail File

Used to validate where and how errors were injected.

Example:

```text
2026-06-09T06-45_export.csv
```

Expected columns:

```text
error_id
rule_id
status
domain
USUBJID
row_index
primitive
variables_modified
re_derived
failure_reason
```

Example `variables_modified`:

```json
{
  "DTHDTC": {
    "original": "2024-04-02",
    "injected": ""
  }
}
```

### 3. Original Dataset Folder

```text
data/input/B01_DM_dates/Original_data/
```

Contains original domain CSV files such as:

```text
DM.csv
AE.csv
EX.csv
```

### 4. Dirty Dataset Folder

```text
data/input/B01_DM_dates/dirty/
```

Contains error-imputed domain CSV files.

### 5. Pinnacle 21 Report

Example:

```text
pinnacle21-report-2026-06-10T12-54-54-618.xlsx
```

Sheets used:

```text
Issue Summary
Rules
```

### 6. SDTM Working Rules Workbook

```text
SDTM_P21_Working_Rules_and_15_Batches 1.xlsx
```

Sheet used:

```text
15 Batches
```

### 7. SDTMIG Rule Test Case Workbook

```text
SDTMIG Rule Test Case 1.xlsx
```

Sheets used:

```text
Study
Test Case
Rule Cases
```

## Validation Logic

### Step 1: Export Summary Validation

The program reads the Export Summary file and extracts all injected Rule IDs.

### Step 2: Export Audit Validation

The program reads the Export Audit Report and extracts:

* Rule ID
* Domain
* USUBJID
* row_index
* primitive
* variables_modified

### Step 3: Original vs Dirty CSV Imputation Check

For each injected rule:

```text
domain = DM
row_index = 41
actual CSV row checked = row_index + 2 = 43
```

The program opens:

```text
Original_data/DM.csv
dirty/DM.csv
```

Then validates the value from `variables_modified`.

Example:

```json
{
  "DTHDTC": {
    "original": "2024-04-02",
    "injected": ""
  }
}
```

The program checks:

```text
Original_data/DM.csv → row 43 → DTHDTC = 2024-04-02
dirty/DM.csv → row 43 → DTHDTC = blank
```

### Step 4: Special Duplicate Row Validation

For duplicate row rules:

```json
{
  "__row__": {
    "original": "unique",
    "injected": "duplicated"
  }
}
```

The program checks:

```text
Original data: USUBJID count = 1
Dirty data: USUBJID count > 1
```

### Step 5: P21 Issue Summary Validation

The program checks whether:

```text
Export Audit rule_id + domain
```

is present in:

```text
P21 Issue Summary → Pinnacle 21 ID + Source
```

### Step 6: P21 Rules Sheet Validation

The program checks whether the Rule ID is present in:

```text
P21 Rules Sheet → Pinnacle 21 ID
```

### Step 7: SDTMIG Rule Test Case Validation

The program checks whether the Rule ID is present in:

```text
Study Sheet
Test Case Sheet
Rule Cases Sheet
```

## Final Validation Status

### PASS

A rule is marked as PASS when:

```text
Injection detail is available
Original vs Dirty imputation match is Yes
Rule ID is present in P21 Issue Summary
Domain matches with P21 Source
```

### FAIL

A rule is marked as FAIL when:

```text
Imputation mismatch
OR Rule ID missing in P21 Issue Summary
OR Domain mismatch
```

### Manual Review

A rule is marked as Manual Review when:

```text
Rule metadata is missing
Required input file is unavailable
Required sheet or column is missing
```

## Output Report

The output Excel report is generated in:

```text
data/output/
```

Example:

```text
B01_DM_dates_validation_report.xlsx
```

Sheets generated:

```text
Rule Validation-B01_DM_dates
Imputation-B01_DM_dates
Missing P21-B01_DM_dates
Count Mismatch-B01_DM_dates
Summary-B01_DM_dates
```

## Installation

Create and activate virtual environment:

```bash
py -3.10 -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run FastAPI:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API Endpoint

```text
POST /validate
```

## Sample Request for B01_DM_dates

```json
{
  "batch_name": "B01_DM_dates",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B01_DM_dates/2026-06-09T06-46_export.csv",
  "export_detail_path": "data/input/B01_DM_dates/2026-06-09T06-45_export.csv",
  "p21_report_path": "data/input/B01_DM_dates/pinnacle21-report-2026-06-10T12-54-54-618.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B01_DM_dates/Original_data",
  "dirty_data_dir": "data/input/B01_DM_dates/dirty"
}
```
## Sample Request for B02_DM_arm_age_flags

```json
{
  "batch_name": "B02_DM_arm_age_flags",
  "host_generator_key": "infectious_disease_covid",
  "export_summary_path": "data/input/B02_DM_arm_age_flags/2026-06-12T05-31_export_summary.csv",
  "export_detail_path": "data/input/B02_DM_arm_age_flags/2026-06-12T05-31_export_Audit_Report.csv",
  "p21_report_path": "data/input/B02_DM_arm_age_flags/pinnacle21-report-2026-06-12T11-11-10-078.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B02_DM_arm_age_flags/Original_data",
  "dirty_data_dir": "data/input/B02_DM_arm_age_flags/dirty"
}
```
## Sample Request for B03_SpecialPurpose_SE_SM_SV_DI

```json
{
  
  "batch_name": "B03_SpecialPurpose_SE_SM_SV_DI",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B03_SpecialPurpose_SE_SM_SV_DI/2026-06-16T05-20_export_summary.csv",
  "export_detail_path": "data/input/B03_SpecialPurpose_SE_SM_SV_DI/2026-06-16T05-19_export_Audit_Report.csv",
  "p21_report_path": "data/input/B03_SpecialPurpose_SE_SM_SV_DI/pinnacle21-report-2026-06-16T10-53-32-782.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B03_SpecialPurpose_SE_SM_SV_DI/Original_data",
  "dirty_data_dir": "data/input/B03_SpecialPurpose_SE_SM_SV_DI/dirty"

}
```
## Sample Request for B04_Interventions
```json
{
  "batch_name": "B04_Interventions",
  "host_generator_key": "respiratory_asthma_gb001",
  "export_summary_path": "data/input/B04_Interventions/2026-06-16T07-41_export_summary.csv",
  "export_detail_path": "data/input/B04_Interventions/2026-06-16T07-41_export_Audit_Report.csv",
  "p21_report_path": "data/input/B04_Interventions/pinnacle21-report-2026-06-16T13-10-01-925.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B04_Interventions/Original_data",
  "dirty_data_dir": "data/input/B04_Interventions/dirty"
}
```

## Sample Request for B05_Events_AE_DS_MH_DV
```json
{
  "batch_name": "B05_Events_AE_DS_MH_DV",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B05_Events_AE_DS_MH_DV/2026-06-16T08-06_export_summary.csv",
  "export_detail_path": "data/input/B05_Events_AE_DS_MH_DV/2026-06-16T08-06_export_Audit_Report.csv",
  "p21_report_path": "data/input/B05_Events_AE_DS_MH_DV/pinnacle21-report-2026-06-16T13-37-51-393.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B05_Events_AE_DS_MH_DV/Original_data",
  "dirty_data_dir": "data/input/B05_Events_AE_DS_MH_DV/dirty"
}
```
## Sample Request for B06_Findings_blank_populate
```json
{
  "batch_name": "B06_Findings_blank_populate",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B06_Findings_blank_populate/2026-06-16T08-40_export_summary.csv",
  "export_detail_path": "data/input/B06_Findings_blank_populate/2026-06-16T08-40_export_Audit_Report.csv",
  "p21_report_path": "data/input/B06_Findings_blank_populate/pinnacle21-report-2026-06-16T14-11-49-523.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B06_Findings_blank_populate/Original_data",
  "dirty_data_dir": "data/input/B06_Findings_blank_populate/dirty"
}
```

## Sample Request for B07_Findings_value_mismatch
```json
{
  "batch_name": "B07_Findings_value_mismatch",
  "host_generator_key": "cardiovascular_hfpef",
  "export_summary_path": "data/input/B07_Findings_value_mismatch/2026-06-16T10-02_export.csv",
  "export_detail_path": "data/input/B07_Findings_value_mismatch/2026-06-16T10-02_export_Audit_Report.csv",
  "p21_report_path": "data/input/B07_Findings_value_mismatch/pinnacle21-report-2026-06-16T15-33-12-227.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B07_Findings_value_mismatch/Original_data",
  "dirty_data_dir": "data/input/B07_Findings_value_mismatch/dirty"
}

```

## Sample Request for B08_Findings_structural
```json
{
  "batch_name": "B08_Findings_structural",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B08_Findings_structural/2026-06-16T10-15_export_summary.csv",
  "export_detail_path": "data/input/B08_Findings_structural/2026-06-16T10-15_export_Audit_Report.csv",
  "p21_report_path": "data/input/B08_Findings_structural/pinnacle21-report-2026-06-16T15-46-41-243.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B08_Findings_structural/Original_data",
  "dirty_data_dir": "data/input/B08_Findings_structural/dirty"
}
```

## Sample Request for B09_AllDomain_columns_and_derived_DY

```json
{
  "batch_name": "B09_AllDomain_columns_and_derived_DY",
  "host_generator_key": "cardiovascular_hfpef",
  "export_summary_path": "data/input/B09_AllDomain_columns_and_derived_DY/2026-06-16T10-27_export_summary.csv",
  "export_detail_path": "data/input/B09_AllDomain_columns_and_derived_DY/2026-06-16T10-28_export_Audit_Report.csv",
  "p21_report_path": "data/input/B09_AllDomain_columns_and_derived_DY/pinnacle21-report-2026-06-16T15-58-51-355.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B09_AllDomain_columns_and_derived_DY/Original_data",
  "dirty_data_dir": "data/input/B09_AllDomain_columns_and_derived_DY/dirty"
}
```

## Sample Request for B10_AllDomain_crossdomain_and_comments
```json
{
  "batch_name": "B10_AllDomain_crossdomain_and_comments",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B10_AllDomain_crossdomain_and_comments/2026-06-16T10-42_export_summary.csv",
  "export_detail_path": "data/input/B10_AllDomain_crossdomain_and_comments/2026-06-16T10-42_export_Audit_Report.csv",
  "p21_report_path": "data/input/B10_AllDomain_crossdomain_and_comments/pinnacle21-report-2026-06-16T16-13-19-241.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B10_AllDomain_crossdomain_and_comments/Original_data",
  "dirty_data_dir": "data/input/B10_AllDomain_crossdomain_and_comments/dirty"
}
```

## Sample Request for B11_Relationship_RELREC_SUPP
```json
{
  "batch_name": "B11_Relationship_RELREC_SUPP",
  "host_generator_key": "cardiovascular_hfpef",
  "export_summary_path": "data/input/B11_Relationship_RELREC_SUPP/2026-06-16T10-56_export_summary.csv",
  "export_detail_path": "data/input/B11_Relationship_RELREC_SUPP/2026-06-16T10-56_export_Audit_Report.csv",
  "p21_report_path": "data/input/B11_Relationship_RELREC_SUPP/pinnacle21-report-2026-06-16T16-27-14-004.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B11_Relationship_RELREC_SUPP/Original_data",
  "dirty_data_dir": "data/input/B11_Relationship_RELREC_SUPP/dirty"
}

```
## Sample Request B12_TrialDesign_TA_TE_TI_TV_TD

```json
{
  "batch_name": "B12_TrialDesign_TA_TE_TI_TV_TD",
  "host_generator_key": "psychiatry_mdd",
  "export_summary_path": "data/input/B12_TrialDesign_TA_TE_TI_TV_TD/2026-06-16T11-19_export_summary.csv",
  "export_detail_path": "data/input/B12_TrialDesign_TA_TE_TI_TV_TD/2026-06-16T11-19_export_Audit_Report.csv",
  "p21_report_path": "data/input/B12_TrialDesign_TA_TE_TI_TV_TD/pinnacle21-report-2026-06-16T16-50-43-485.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B12_TrialDesign_TA_TE_TI_TV_TD/Original_data",
  "dirty_data_dir": "data/input/B12_TrialDesign_TA_TE_TI_TV_TD/dirty"
}
```

## Sample Request for B13_TrialSummary_TS_part1

```json
{
  "batch_name": "B13_TrialSummary_TS_part1",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B13_TrialSummary_TS_part1/2026-06-16T11-30_export_summary.csv",
  "export_detail_path": "data/input/B13_TrialSummary_TS_part1/2026-06-16T11-30_export_Audit_Report.csv",
  "p21_report_path": "data/input/B13_TrialSummary_TS_part1/pinnacle21-report-2026-06-16T17-02-54-054.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B13_TrialSummary_TS_part1/Original_data",
  "dirty_data_dir": "data/input/B13_TrialSummary_TS_part1/dirty"
}
```
## Sample Request for B14_TrialSummary_TS_part2
```json

{
  "batch_name": "B14_TrialSummary_TS_part2",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B14_TrialSummary_TS_part2/2026-06-16T11-39_export_summary.csv",
  "export_detail_path": "data/input/B14_TrialSummary_TS_part2/2026-06-16T11-40_export_Audit_Report.csv",
  "p21_report_path": "data/input/B14_TrialSummary_TS_part2/pinnacle21-report-2026-06-16T17-11-59-631.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B14_TrialSummary_TS_part2/Original_data",
  "dirty_data_dir": "data/input/B14_TrialSummary_TS_part2/dirty"
}

```
## Sample Request for 
```json
{
  "batch_name": "B15_TrialSummary_TS_part3",
  "host_generator_key": "oncology_nsclc",
  "export_summary_path": "data/input/B15_TrialSummary_TS_part3/2026-06-16T11-48_export_summary.csv",
  "export_detail_path": "data/input/B15_TrialSummary_TS_part3/2026-06-16T11-48_export_Audit_Report.csv",
  "p21_report_path": "data/input/B15_TrialSummary_TS_part3/pinnacle21-report-2026-06-16T17-20-21-369.xlsx",
  "working_rules_path": "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx",
  "test_case_path": "data/input/SDTMIG Rule Test Case 1.xlsx",
  "original_data_dir": "data/input/B15_TrialSummary_TS_part3/Original_data",
  "dirty_data_dir": "data/input/B15_TrialSummary_TS_part3/dirty"
}

```
## Notes

* `row_index + 2` is used to identify the actual CSV row being validated.
* Blank injected values are handled correctly using `keep_default_na=False`.
* Dates are normalized before comparison.
* Count Match is kept only as an informational column and does not decide final PASS/FAIL.
* Final PASS/FAIL depends mainly on imputation result, P21 Issue Summary presence, and domain match.
