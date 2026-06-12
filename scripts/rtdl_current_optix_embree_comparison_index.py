#!/usr/bin/env python3
"""Emit the current OptiX-vs-Embree comparability index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.current_optix_embree_comparison_index import (  # noqa: E402
    current_optix_embree_comparison_index,
)


def _markdown(payload: dict[str, object]) -> str:
    rows = payload["rows"]
    assert isinstance(rows, tuple)
    lines = [
        "# Current OptiX vs Embree Comparison Index",
        "",
        f"Version: `{payload['version']}`",
        "",
        "This is a comparability index, not a speedup table and not a public speedup table.",
        "",
        "Goal4341 supersedes this planning index for the optimized LibRTS AABB "
        "same-contract row. This Goal4338 index remains useful for showing why "
        "the older broad registry artifacts should not be compared directly.",
        "",
        "| App | OptiX row | Embree CPU row | Existing artifact status | Comparability | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_obj in rows:
        row = dict(row_obj)
        optix = dict(row["optix"])
        embree = dict(row["embree_cpu"])
        optix_artifact = dict(optix["artifact"])
        embree_artifact = dict(embree["artifact"])
        status = "OptiX {0}; Embree {1}".format(
            optix_artifact["status"],
            embree_artifact["status"],
        )
        lines.append(
            "| {app} | `{optix_row}` | `{embree_row}` | {status} | {klass} | {next_action} |".format(
                app=row["app"],
                optix_row=optix["row_id"],
                embree_row=embree["row_id"],
                status=status,
                klass=row["comparison_class"],
                next_action=row["required_next_action"],
            )
        )
    lines.extend(
        [
            "",
            "RTNN artifact mismatch remains visible here because the current registry "
            "expects the Goal4308 Embree row while the older artifact packet may not "
            "contain that row.",
            "",
            "Every row keeps `ratio_authorized_from_existing_artifacts` false.",
            "Fresh same-contract paired runs are required before publishing backend speedups.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output-json", type=Path, help="write JSON to this path")
    args = parser.parse_args(argv)

    payload = current_optix_embree_comparison_index()
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_markdown(payload), end="")
    return 0 if payload["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
