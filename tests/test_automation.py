import logging

from app.services.automation_service import AutomationService
from app.services.batch_config_service import BatchConfigService

logger = logging.getLogger(__name__)


def test_automation():

    config = BatchConfigService().get_batch_configuration(
        "B01_DM_dates",
    )

    AutomationService().run_batch(
        config,
    )


if __name__ == "__main__":

    test_automation()