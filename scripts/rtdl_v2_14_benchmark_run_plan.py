#!/usr/bin/env python3
"""Emit the executable v2.14 benchmark run plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v2_14_benchmark_run_plan import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_OVERLAY_DATASET_ROOT,
    DEFAULT_RAYJOIN_POLYOVER_EXEC,
    DEFAULT_RAYJOIN_QUERY_EXEC,
    markdown_v2_14_benchmark_run_plan,
    v2_14_benchmark_run_plan_packet,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output-json", type=Path, help="write JSON to this path")
    parser.add_argument("--output-markdown", type=Path, help="write Markdown report to this path")
    parser.add_argument("--python-executable", default="python3")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--overlay-dataset-root", default=DEFAULT_OVERLAY_DATASET_ROOT)
    parser.add_argument("--rayjoin-query-exec", default=DEFAULT_RAYJOIN_QUERY_EXEC)
    parser.add_argument("--rayjoin-polyover-exec", default=DEFAULT_RAYJOIN_POLYOVER_EXEC)
    parser.add_argument("--overlay-pairs", help="comma-separated Section 5.7 overlay pair ids; default is all 8")
    args = parser.parse_args(argv)

    payload = v2_14_benchmark_run_plan_packet(
        python_executable=args.python_executable,
        output_dir=args.output_dir,
        overlay_dataset_root=args.overlay_dataset_root,
        rayjoin_query_exec=args.rayjoin_query_exec,
        rayjoin_polyover_exec=args.rayjoin_polyover_exec,
        overlay_pairs=args.overlay_pairs,
    )
    markdown = markdown_v2_14_benchmark_run_plan(payload)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.output_markdown:
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(markdown, end="")
    return 0 if payload["validation"]["status"] == "accept_executable_plan" else 1


if __name__ == "__main__":
    raise SystemExit(main())

