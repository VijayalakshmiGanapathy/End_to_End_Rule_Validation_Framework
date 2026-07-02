import logging

from app.core.paths import BatchPaths
from app.services.batch_config_service import BatchConfigService
from app.services.p21_service import P21Service

logger = logging.getLogger(__name__)


def test_p21():

    config = BatchConfigService().get_batch_configuration(
        "B01_DM_dates",
    )

    paths = BatchPaths(
        config.batch_name,
    )

    paths.create()

    report = (
        paths.p21_reports /
        "P21_B01_DM_dates_Run1.xlsx"
    )

    P21Service().run(
        paths.dirty,
        report,
    )


if __name__ == "__main__":

    test_p21()