from __future__ import annotations

from examples.benchmark_apps._support._repo_bootstrap import ensure_repo_src_on_path

ensure_repo_src_on_path()

from rtdsl._example_support.benchmark_harness_compat import run_archived_harness


def main() -> int:
    return run_archived_harness("spatial_rayjoin")


if __name__ == "__main__":
    raise SystemExit(main())
