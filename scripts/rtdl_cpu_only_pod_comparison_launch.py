#!/usr/bin/env python3
"""Emit the Goal4346 CPU-only OptiX-vs-Embree pod launch packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.cpu_only_pod_comparison_launch import cpu_only_pod_comparison_launch_packet  # noqa: E402


def _cmd(command: tuple[str, ...]) -> str:
    return " ".join(command)


def _markdown(payload: dict[str, object]) -> str:
    optix = dict(payload["optix_scale_command"])
    rows = tuple(payload["embree_cpu_scale_commands"])
    blockers = tuple(payload["contract_choice_blockers"])
    summary = dict(payload["current_comparison_summary"])
    lines = [
        "# Goal4346: CPU-Only Pod Comparison Launch",
        "",
        "Date: 2026-06-11",
        "",
        "Status: CPU-only OptiX-vs-Embree launch packet; not release or public speedup authorization.",
        "",
        "## Verdict",
        "",
        "Proceed with NVIDIA RT-core OptiX versus Embree CPU only. No Intel-GPU lane is included.",
        "",
        "Run OptiX on an RTX-class pod. Do not use Pascal/GTX hardware for RT-core timing.",
        "",
        "## Preflight",
        "",
    ]
    for line in payload["environment_prefix"]:
        lines.append(f"`{line}`")
    lines.extend(
        [
            "",
            "## OptiX Pod Command",
            "",
            f"`{_cmd(tuple(optix['command']))}`",
            "",
            "## Embree CPU Commands",
            "",
            "| App | Bucket | Output | Command |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row_obj in rows:
        row = dict(row_obj)
        lines.append(
            "| {app} | `{bucket}` | `{output}` | `{command}` |".format(
                app=row["app"],
                bucket=row["bucket"],
                output=row["output_json"],
                command=_cmd(tuple(row["command"])),
            )
        )
    lines.extend(
        [
            "",
            "## Contract-Choice Blockers",
            "",
            "| App | Reason | Next Action |",
            "| --- | --- | --- |",
        ]
    )
    for row_obj in blockers:
        row = dict(row_obj)
        lines.append(f"| {row['app']} | {row['reason']} | {row['next_action']} |")
    lines.extend(
        [
            "",
            "## Current Comparison Shape",
            "",
        ]
    )
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Postprocess",
            "",
        ]
    )
    for command in payload["postprocess_commands"]:
        lines.append(f"`{_cmd(tuple(command))}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            str(payload["claim_boundary"]),
            "",
            "Validation status: `{}`.".format(dict(payload["validation"])["status"]),
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output-json", type=Path, help="write JSON to this path")
    parser.add_argument("--output-markdown", type=Path, help="write Markdown report to this path")
    args = parser.parse_args(argv)

    payload = cpu_only_pod_comparison_launch_packet()
    markdown = _markdown(payload)
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
    return 0 if payload["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
