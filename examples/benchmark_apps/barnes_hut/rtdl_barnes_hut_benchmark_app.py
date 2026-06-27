from __future__ import annotations

from examples.benchmark_apps._support.archived_harness_runner import (
    load_archived_harness_module,
    run_archived_harness,
)


_ARCHIVED = load_archived_harness_module("barnes_hut", __name__ + "._archived")
globals().update(
    {
        name: value
        for name, value in vars(_ARCHIVED).items()
        if not (name.startswith("__") and name not in {"__doc__", "__all__"})
    }
)


def main() -> int:
    return run_archived_harness("barnes_hut")


if __name__ == "__main__":
    raise SystemExit(main())
