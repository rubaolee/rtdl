from __future__ import annotations

from examples.benchmark_apps._support.archived_harness_runner import load_archived_harness_module


_ARCHIVED = load_archived_harness_module("hausdorff_v2_function", __name__ + "._archived")
globals().update(
    {
        name: value
        for name, value in vars(_ARCHIVED).items()
        if not (name.startswith("__") and name not in {"__doc__", "__all__"})
    }
)
