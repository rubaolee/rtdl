from __future__ import annotations

from examples.benchmark_apps._support.archived_harness_runner import run_archived_harness


def main() -> int:
    return run_archived_harness("barnes_hut")


if __name__ == "__main__":
    raise SystemExit(main())
