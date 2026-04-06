from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate one runnable RTDL program without executing the workload locally.")
    parser.add_argument("--workload", choices=("segment_polygon_hitcount",), required=True)
    parser.add_argument(
        "--dataset",
        choices=(
            "authored_segment_polygon_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb",
            "derived/br_county_subset_segment_polygon_tiled_x4",
        ),
        required=True,
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix"),
        default="cpu",
    )
    parser.add_argument("--output-mode", choices=("rows", "summary"), default="rows")
    parser.add_argument("--no-verify", action="store_true", help="omit the generated verification block invocation")
    parser.add_argument("--output", required=True, help="where to write the generated Python file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = rt.generate_python_program(
        rt.GenerateOnlyRequest(
            workload=args.workload,
            dataset=args.dataset,
            backend=args.backend,
            verify=not args.no_verify,
            output_mode=args.output_mode,
        ),
        args.output,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
