from app.services.test_approach2.automation_service_t2 import (
    AutomationService,
)


def test_automation_t2():

    AutomationService().run_all_batches()


if __name__ == "__main__":

    test_automation_t2()