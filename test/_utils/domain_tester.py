from components.lib.smorest_router.smorest_router import SmorestRouter
from components.lib.storage_manager import StorageManager


class DomainTester:
    def __init__(
        self,
        router: SmorestRouter,
        storage: StorageManager,
    ) -> None:
        self.router = router
        self.storage = storage

    def tester(self):
        return self.router.tester()

    def context(self):
        return self.router.app.app_context()
