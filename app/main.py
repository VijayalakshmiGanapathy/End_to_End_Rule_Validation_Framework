from fastapi import FastAPI
from app.api.validation_routes import router as validation_router
from app.core.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="Rule Injection Verification Framework",
    version="1.0.0",
    description="Validates SDTMIG rule imputation against P21 and SDTM rule test case reports.",
)

app.include_router(validation_router)
