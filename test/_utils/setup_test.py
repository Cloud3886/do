import logging
import shutil
import subprocess
from pathlib import Path


def run_cmd(cmd: str):
    process = subprocess.run(cmd.split(" "), capture_output=True)
    if process.stdout:
        logging.warning(process.stdout.decode())
    if process.stderr:
        logging.error(process.stderr.decode())


class SetupTests:
    def __init__(self) -> None:
        self.base_dir = self.setup_base_dir()

    def setup_base_dir(self) -> str:
        logging.warning("Removing DB Records")
        base_dir = "_test_records/records"
        shutil.rmtree(base_dir, ignore_errors=True)
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        return base_dir

    def setup_db(self, test: str = "test") -> str:
        test_dir = self._setup_test(test)
        return f"{test_dir}/db.sqlite"

    def setup_redis(self, test: str = "test") -> int:
        test_dir = self._setup_test(test)
        port = 7694
        run_cmd(
            "redis-server"
            f" --port {port}"
            " --daemonize yes"
            f" --pidfile ./redis_test_{port}.pid"
            " --loglevel debug"
            " --logfile redis.log"
            " --dbfilename redis.rdb"
            f" --dir ./{test_dir}/"
        )
        return port

    def cleanup_redis(self, port: int):
        run_cmd(f"redis-cli -p {port} shutdown now force")

    def _setup_test(self, test: str) -> str:
        test_name = test.split("[")[0]
        test_id = test.removeprefix(test_name).removeprefix("[").removesuffix("]")
        test_dir = f"{self.base_dir}/{test_name}"
        if test_id:
            test_dir += "/" + test_id
        Path(test_dir).mkdir(parents=True, exist_ok=True)
        return test_dir
