from fastapi import APIRouter, HTTPException

from app.exceptions.custom_exceptions import ValidationFrameworkError
from app.models.validation_request import ValidationRequest
from app.services.validation_service import ValidationService

router = APIRouter(tags=["Validation"])


@router.post("/validate")
def validate_rule_injection(request: ValidationRequest) -> dict:
    """Run batch-level rule injection validation."""
    try:
        service = ValidationService(request)
        output_path = service.run_validation()
        return {
            "status": "success",
            "message": "Validation completed successfully.",
            "output_report": output_path,
        }
    except ValidationFrameworkError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
