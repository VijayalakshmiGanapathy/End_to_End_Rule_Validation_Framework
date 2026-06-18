import logging
from pathlib import Path

import pandas as pd

from app.exceptions.custom_exceptions import FileReadError, SheetNotFoundError

logger = logging.getLogger(__name__)


def read_csv_file(file_path: str) -> pd.DataFrame:
    """Read a CSV file and return a DataFrame."""
    path = Path(file_path)
    try:
        logger.info("Reading CSV file: %s", path)
        return pd.read_csv(path)
    except Exception as exc:
        raise FileReadError(f"Unable to read CSV file: {path}") from exc


def read_excel_sheet(file_path: str, sheet_name: str) -> pd.DataFrame:
    """Read a specific Excel sheet and return a DataFrame."""
    path = Path(file_path)
    try:
        logger.info("Reading Excel file: %s | sheet: %s", path, sheet_name)
        if sheet_name == "Issue Summary":
            return pd.read_excel(path, sheet_name=sheet_name, skiprows=3)

        return pd.read_excel(path, sheet_name=sheet_name)
    
    except ValueError as exc:
        raise SheetNotFoundError(
            f"Sheet '{sheet_name}' not found in workbook: {path}"
        ) from exc
    except Exception as exc:
        raise FileReadError(f"Unable to read Excel file: {path}") from exc
