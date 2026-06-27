from __future__ import annotations

from examples.benchmark_apps._support._repo_bootstrap import ensure_repo_src_on_path

ensure_repo_src_on_path()

from rtdsl._example_support.benchmark_harness_compat import (
    load_archived_harness_module,
    run_archived_harness,
)


_ARCHIVED = load_archived_harness_module("raydb_style", __name__ + "._archived")
globals().update(
    {
        name: value
        for name, value in vars(_ARCHIVED).items()
        if not (name.startswith("__") and name not in {"__doc__", "__all__"})
    }
)


def main() -> int:
    return run_archived_harness("raydb_style")


if __name__ == "__main__":
    raise SystemExit(main())
