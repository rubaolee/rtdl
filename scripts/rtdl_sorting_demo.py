from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.internal.rtdl_sorting import expected_hit_counts
from examples.internal.rtdl_sorting import quicksort_reference
from examples.internal.rtdl_sorting import run_sorting_backend
from examples.internal.rtdl_sorting import stable_sort_reference


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the RTDL sorting example on one backend.")
    parser.add_argument("--backend", choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"), default="cpu_python_reference")
    parser.add_argument("values", nargs="*", type=int, help="nonnegative integers to sort")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    values = tuple(args.values)
    result = run_sorting_backend(args.backend, values)
    payload = {
        "backend": args.backend,
        "values": values,
        "hit_counts": result["hit_counts"],
        "ascending_from_hits": result["ascending"],
        "descending_from_hits": result["descending"],
        "ascending_sorted_reference": stable_sort_reference(values),
        "descending_sorted_reference": stable_sort_reference(values, descending=True),
        "ascending_quicksort_reference": quicksort_reference(values),
        "descending_quicksort_reference": quicksort_reference(values, descending=True),
        "expected_hit_counts": expected_hit_counts(values),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
