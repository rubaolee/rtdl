from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_rt_barneshut_author_route import (  # noqa: E402
    run_v4_rt_barneshut_external_author_rt_core_route,
    validate_v4_rt_barneshut_author_route_result,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run V4's same-semantics RT-BarnesHut external author RT-core "
            "reference route. This is not a native V4 operator speed claim."
        )
    )
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--file-type", required=True, choices=("treelogy", "csv"))
    parser.add_argument("--limit", required=True, type=int)
    parser.add_argument("--author-binary", required=True, type=Path)
    parser.add_argument("--author-command-prefix", nargs="*", default=())
    parser.add_argument("--trimmed-dataset", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    result = run_v4_rt_barneshut_external_author_rt_core_route(
        dataset=args.dataset,
        file_type=args.file_type,
        limit=args.limit,
        author_binary=args.author_binary,
        trimmed_dataset=args.trimmed_dataset,
        author_command_prefix=tuple(args.author_command_prefix),
    )
    validate_v4_rt_barneshut_author_route_result(result)
    payload = result.as_dict()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
