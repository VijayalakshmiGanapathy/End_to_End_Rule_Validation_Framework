from app.services.batch_config_service import (
    BatchConfigService,
)


def test_batch_configuration():

    service = BatchConfigService()

    config = service.get_batch_configuration(
        "B01_DM_dates"
    )

    print()

    print("Batch Name")

    print(config.batch_name)

    print()

    print("Host Generator Key")

    print(config.host_generator_key)

    print()

    print("Rule IDs")

    for rule in config.rule_ids:

        print(rule)


if __name__ == "__main__":

    test_batch_configuration()