from __future__ import annotations

import time
from pathlib import Path

from pecs.runtime.runtime_core import (
    RuntimeCore,
)


class LiveContinuityDaemon:
    def __init__(
        self,
        project_root: str,
        interval: int = 30,
    ):
        self.project_root = Path(
            project_root
        )

        self.interval = interval

        self.runtime = RuntimeCore(
            str(project_root)
        )

    def cycle(
        self,
    ):
        return self.runtime.run()

    def start(
        self,
    ):
        while True:
            self.cycle()

            time.sleep(
                self.interval
            )


if __name__ == "__main__":
    root = Path.cwd()

    daemon = LiveContinuityDaemon(
        str(root)
    )

    daemon.start()
