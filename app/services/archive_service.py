from pathlib import Path
import shutil
import zipfile


class ArchiveService:
    """
    Generic Archive Service.

    Supports:
        • TrialGen ZIP extraction
        • Injection Harness Dirty ZIP extraction
    """

    @staticmethod
    def extract_archive(
        zip_file: Path,
        extract_to: Path,
        clean_folder: str | None = None,
    ):
        """
        Extract a ZIP archive.

        Parameters
        ----------
        zip_file : Path
            ZIP archive.

        extract_to : Path
            Destination folder.

        clean_folder : str | None
            Optional subfolder to delete before extraction.
            Examples:
                "dirty"
                "Original_data"
        """

        extract_to.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -----------------------------------------
        # Delete previous folder if required
        # -----------------------------------------

        if clean_folder:

            folder = extract_to / clean_folder

            if folder.exists():

                print(
                    f"Deleting existing folder : {folder}"
                )

                shutil.rmtree(folder)

                print(
                    f"{clean_folder} deleted successfully."
                )

        # -----------------------------------------
        # Extract ZIP
        # -----------------------------------------

        print(
            f"Extracting : {zip_file.name}"
        )

        with zipfile.ZipFile(
            zip_file,
            "r",
        ) as archive:

            archive.extractall(
                extract_to,
            )

        print(
            "Extraction completed successfully."
        )

    @staticmethod
    def verify_extraction(
        folder: Path,
        expected_count: int = 26,
    ):
        """
        Verify extracted CSV files.

        Parameters
        ----------
        folder : Path
            Folder containing CSV files.

        expected_count : int
            Expected number of CSV files.
        """

        if not folder.exists():

            raise Exception(
                f"{folder.name} folder was not created."
            )

        csv_files = list(
            folder.glob("*.csv")
        )

        if len(csv_files) != expected_count:

            raise Exception(
                f"Expected {expected_count} CSV files, "
                f"found {len(csv_files)}."
            )

        print(
            f"{len(csv_files)} CSV files extracted successfully."
        )

    @staticmethod
    def delete_archive(
        zip_file: Path,
    ):
        """
        Delete ZIP archive.
        """

        if zip_file.exists():

            zip_file.unlink()

            print(
                f"{zip_file.name} deleted successfully."
            )

    @staticmethod
    def verify_trialgen_extraction(
        original_data_folder: Path,
    ):

        csv_files = list(
            original_data_folder.glob("*.csv")
        )

        if not csv_files:

            raise Exception(
                "No TrialGen CSV files extracted."
            )

        print(
            f"{len(csv_files)} TrialGen CSV files extracted."
        )

    @staticmethod
    def verify_dirty_extraction(
        dirty_folder: Path,
    ):
        """
        Verify dirty CSV extraction.
        """

        if not dirty_folder.exists():

            raise Exception(
                "Dirty folder was not created."
            )

        csv_files = list(
            dirty_folder.glob("*.csv")
        )

        if not csv_files:

            raise Exception(
                "No dirty CSV files extracted."
            )

        print(
            f"{len(csv_files)} Dirty CSV files extracted successfully."
        )