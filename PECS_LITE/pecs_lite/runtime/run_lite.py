from pathlib import Path

from pecs_lite.runtime.pecs_lite_runtime_core import (
    PECSLiteRuntimeCore,
)

if __name__ == "__main__":
    root = Path.cwd()

    runtime = PECSLiteRuntimeCore(
        str(root)
    )

    payload = runtime.run()

    print(payload)
