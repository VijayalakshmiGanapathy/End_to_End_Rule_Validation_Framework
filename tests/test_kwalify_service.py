from app.core.paths import BatchPaths
from app.services.batch_config_service import BatchConfigService
from app.services.kwalify_service import KwalifyService


def test_kwalify():

    config = BatchConfigService().get_batch_configuration(
        "B01_DM_dates"
    )

    paths = BatchPaths(
        config.batch_name,
    )

    run_id = KwalifyService().run(
        paths,
        config,
        run_number=1,
    )

    print(run_id)


if __name__ == "__main__":
    test_kwalify()