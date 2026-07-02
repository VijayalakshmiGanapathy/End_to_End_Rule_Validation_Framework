import logging
import subprocess
import time
from pathlib import Path


import re

from app.core.config import (
    JAVA_EXE,
    P21_JAR,
    ENGINE_VERSION,
    CONFIG_XML,
    STANDARD,
    STANDARD_VERSION,
)

logger = logging.getLogger(__name__)


class P21Service:
    """
    Executes Pinnacle21 CLI validation.
    """

    def __init__(self):
        pass

    def build_command(
        self,
        source_folder: Path,
        output_file: Path,
    ):

        return [
            str(JAVA_EXE),
            "-jar",
            str(P21_JAR),
            f"--engine.version={ENGINE_VERSION}",
            f"--config={CONFIG_XML}",
            f"--standard={STANDARD}",
            f"--standard.version={STANDARD_VERSION}",
            f"--source.sdtm={source_folder}",
            f"--report={output_file}",
        ]
    
    

    def get_next_report_file(
        self,
        #report_folder: Path,
        paths,
    ) -> Path:
        """
        Returns the next P21 report filename.

        Example:
            P21_B01_Run1.xlsx
            P21_B01_Run2.xlsx
        """
        report_folder = paths.p21_reports

        report_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        run_numbers = []

        

        pattern = re.compile(
            rf"P21_{re.escape(paths.batch_prefix)}_Run(\d+)\.xlsx$",
            re.IGNORECASE,
        )

        for file in report_folder.glob("*.xlsx"):

            match = pattern.match(file.name)

            if match:

                run_numbers.append(
                    int(match.group(1))
                )

        next_run = (
            max(run_numbers) + 1
            if run_numbers
            else 1
        )

        

        report_file = (
            report_folder
            / f"P21_{paths.batch_prefix}_Run{next_run}.xlsx"
        )

        return report_file, next_run
    
    def run(
        self,
        source_folder: Path,
        output_file: Path,
    ):
        """
        Execute Pinnacle21 CLI.
        """

        command = self.build_command(
            source_folder,
            output_file,
        )

        logger.info("Starting Pinnacle21 Validation...")

        logger.info("Command:")

        for item in command:
            logger.info(item)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        report_created = output_file.exists()

        process_completed = (
            "Process completed" in result.stdout
        )

        success = (
            report_created
            and process_completed
        )

        if success:

            logger.info(
                f"P21 Report Generated : {output_file.name}"
            )

            
            logger.info(
                "P21 Validation Completed Successfully."
            )

        else:

            logger.error(
                "P21 Validation Failed."
            )

            if result.stderr.strip():

                logger.error(result.stderr.strip())

        return {
            "success": report_created,
            "output_file": output_file,
            "return_code": result.returncode,
            "report_size": output_file.stat().st_size if report_created else 0,
        }