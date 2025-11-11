from redis import Redis

from components.lib.storage_manager.database_manager import DatabaseManager


class StorageManager:
    def __init__(
        self,
        debug: bool = False,
        db: DatabaseManager | None = None,
        redis: Redis | None = None,
    ) -> None:
        self.debug = debug

        self.db: DatabaseManager
        if db:
            self.db = db

        self.redis: Redis
        if redis:
            self.redis = redis
