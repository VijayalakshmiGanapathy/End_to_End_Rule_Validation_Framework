from fastapi import FastAPI
from app.api.validation_routes import router as validation_router
from app.core.logging_config import configure_logging
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.models.validation_request import ValidationRequest
from app.services.validation_service import ValidationService
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.injection_harness_service import InjectionHarnessService

import pandas as pd

configure_logging()

app = FastAPI(
    title="Rule Injection Verification Framework",
    version="1.0.0",
    description="Validates SDTMIG rule imputation against P21 and SDTM rule test case reports.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/batch-options")
def get_batch_options():
    working_rules_path = "\data\input\Error_Injector_Working_Rule_Batches.xlsx"

    df = pd.read_excel(
        working_rules_path,
        sheet_name="Batches",
    )

    df.columns = df.columns.str.strip()

    df = df[["Batch", "Host Generator Key"]].dropna().drop_duplicates()

    options = []

    for _, row in df.iterrows():
        options.append(
            {
                "batch_name": str(row["Batch"]).strip(),
                "host_generator_key": str(row["Host Generator Key"]).strip(),
            }
        )

    return options

def find_file(folder: Path, pattern: str) -> str:
    files = list(folder.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No file found for pattern: {pattern}")

    return str(files[0])


@app.post("/validate-batch")

def validate_batch(request: dict):
    batch_name = request["batch_name"]
    host_generator_key = request["host_generator_key"]

    batch_folder = Path("data/input") / batch_name

    export_summary_path = find_file(batch_folder, "*export_summary.csv")
    export_detail_path = find_file(batch_folder, "*export_Audit_Report.csv")
    p21_report_path = find_file(batch_folder, "pinnacle21-report*.xlsx")

    validation_request = ValidationRequest(
        batch_name=batch_name,
        host_generator_key=host_generator_key,
        export_summary_path=export_summary_path,
        export_detail_path=export_detail_path,
        p21_report_path=p21_report_path,
        working_rules_path=(
            "data/input/SDTM_P21_Working_Rules_and_15_Batches 1.xlsx"
        ),
        test_case_path="data/input/SDTMIG Rule Test Case 1.xlsx",
        original_data_dir=str(batch_folder / "Original_data"),
        dirty_data_dir=str(batch_folder / "dirty"),
    )

    output_path = ValidationService(validation_request).run_validation()

    return {
        "message": "Validation completed successfully",
        "output_path": output_path,
    }


class InjectionRequest(BaseModel):
    batch_name: str
    host_generator_key: str


@app.post("/run-injection")
def run_injection_api(request: InjectionRequest):
    try:
        service = InjectionHarnessService()

        result = service.run(
            batch_name=request.batch_name,
            host_generator_key=request.host_generator_key,
        )

        return {
            "success": True,
            "message": "Injection completed successfully.",
            "data": result,
        }

    except Exception as ex:
        return {
            "success": False,
            "message": str(ex),
        }
    

frontend_dist = Path("frontend/dist")

if frontend_dist.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=frontend_dist / "assets"),
        name="assets",
    )

    @app.get("/")
    def serve_react_app():
        return FileResponse(frontend_dist / "index.html")

app.include_router(validation_router)
