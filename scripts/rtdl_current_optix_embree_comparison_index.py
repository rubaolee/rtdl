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
        "Goal4341 supersedes the older planning index for the optimized LibRTS "
        "AABB same-contract row. Goal4358 now adds Spatial RayJoin LSI/PIP "
        "same-stream scalar-count pairs. This current index remains useful for "
        "showing which broad registry artifacts should not be compared directly.",
        "",
        "| App | OptiX row | Embree CPU row | Existing artifact status | Comparability | Internal ratio scope | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
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
            "| {app} | `{optix_row}` | `{embree_row}` | {status} | {klass} | `{scope}` | {next_action} |".format(
                app=row["app"],
                optix_row=optix["row_id"],
                embree_row=embree["row_id"],
                status=status,
                klass=row["comparison_class"],
                scope=row["ratio_authorization_scope"],
                next_action=row["required_next_action"],
            )
        )
        same_stream_pairs = tuple(row.get("same_stream_scalar_count_pairs") or ())
        if same_stream_pairs:
            for pair_obj in same_stream_pairs:
                pair = dict(pair_obj)
                lines.append(
                    "| {app} / {workload} | `Goal4358 OptiX` | `Goal4358 Embree` | count {count}, match={match} | same-stream scalar-count pair | `{scope}` | OptiX {optix_ms:.3f} ms vs Embree {embree_ms:.3f} ms; OptiX/Embree speedup {speedup:.2f}x |".format(
                        app=row["app"],
                        workload=pair["workload"],
                        count=int(pair["row_count"]),
                        match=bool(pair["cross_backend_count_match"]),
                        scope=pair["ratio_authorization"],
                        optix_ms=float(pair["optix_hot_query_ms"]),
                        embree_ms=float(pair["embree_hot_query_ms"]),
                        speedup=float(pair["optix_faster_than_embree"]),
                    )
                )
    lines.extend(
        [
            "",
            "RTNN artifact mismatch remains visible here because the current registry "
            "expects the Goal4308 Embree row while the older artifact packet may not "
            "contain that row.",
            "",
            "Only the Goal4358 Spatial RayJoin LSI/PIP same-stream scalar-count "
            "pairs authorize internal backend ratios from existing artifacts. "
            "Every public/release speedup claim flag remains false.",
            "Fresh same-contract paired runs are still required before publishing "
            "whole-app or broad benchmark speedups.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output-json", type=Path, help="write JSON to this path")
    parser.add_argument("--output-markdown", type=Path, help="write Markdown report to this path")
    args = parser.parse_args(argv)

    payload = current_optix_embree_comparison_index()
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown = _markdown(payload)
    if args.output_markdown:
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(markdown, end="")
    return 0 if payload["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
