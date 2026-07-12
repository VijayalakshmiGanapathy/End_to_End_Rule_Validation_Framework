from dataclasses import dataclass

import pandas as pd

from app.core.config import WORKING_RULES_FILE


@dataclass
class BatchConfiguration:

    batch_name: str

    

    rule_ids: list[str]


class BatchConfigService:
    """Read batch configuration from Working Rules Excel."""

    def __init__(self):

        self.df = pd.read_excel(
            WORKING_RULES_FILE,
            sheet_name="Batches_Manual",
        )

        self.df.columns = (
            self.df.columns
            .str.strip()
        )

    def get_batch_configuration(
        self,
        batch_name: str,
    ) -> BatchConfiguration:

        filtered_df = self.df[
            self.df["Batch"]
            .astype(str)
            .str.strip()
            == batch_name
        ]

        if filtered_df.empty:

            raise ValueError(
                f"Batch '{batch_name}' not found."
            )

        

        rule_ids = (
            filtered_df["Rule ID"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .unique()
            .tolist()
        )

        return BatchConfiguration(
            batch_name=batch_name,
            rule_ids=rule_ids,
        )
    
    def get_all_batches(self):
        """
        Returns BatchConfiguration objects for every unique batch
        in the Batches sheet.
        """

        batch_names = (
            self.df["Batch"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        configs = []

        for batch_name in batch_names:

            configs.append(
                self.get_batch_configuration(batch_name)
            )

        return configs