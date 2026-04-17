#!/usr/bin/env python3
"""Goal497 public-entry smoke checks for RTDL docs and examples."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_DOCS = [
    "README.md",
    "docs/README.md",
    "docs/current_architecture.md",
    "docs/capability_boundaries.md",
    "docs/quick_tutorial.md",
    "docs/tutorials/feature_quickstart_cookbook.md",
    "docs/release_facing_examples.md",
    "examples/README.md",
    "docs/features/README.md",
    "docs/rtdl_feature_guide.md",
    "docs/tutorials/README.md",
    "docs/tutorials/db_workloads.md",
    "docs/tutorials/graph_workloads.md",
    "history/COMPLETE_HISTORY.md",
    "history/revision_dashboard.md",
]

SMOKE_COMMANDS = [
    {
        "name": "hello_world",
        "cmd": [sys.executable, "examples/rtdl_hello_world.py"],
    },
    {
        "name": "geometry_segment_polygon",
        "cmd": [
            sys.executable,
            "examples/rtdl_segment_polygon_hitcount.py",
            "--backend",
            "cpu_python_reference",
            "--copies",
            "16",
        ],
    },
    {
        "name": "feature_quickstart_cookbook",
        "cmd": [sys.executable, "examples/rtdl_feature_quickstart_cookbook.py"],
    },
    {
        "name": "graph_bfs",
        "cmd": [
            sys.executable,
            "examples/rtdl_graph_bfs.py",
            "--backend",
            "cpu_python_reference",
        ],
    },
    {
        "name": "db_conjunctive_scan",
        "cmd": [
            sys.executable,
            "examples/rtdl_db_conjunctive_scan.py",
            "--backend",
            "cpu_python_reference",
        ],
    },
    {
        "name": "db_app_auto",
        "cmd": [
            sys.executable,
            "examples/rtdl_v0_7_db_app_demo.py",
            "--backend",
            "auto",
        ],
    },
]

REQUIRED_PHRASES = {
    "README.md": [
        "10x reduction in workload-writing burden",
        "not an unbounded speedup claim",
        "RTDL is not a DBMS",
        "RTDL v0.7 Support Matrix",
    ],
    "docs/current_architecture.md": [
        "10x reduction in authoring burden",
        "This is not a blanket performance claim",
        "RTDL is still not a DBMS",
    ],
    "docs/capability_boundaries.md": [
        "Can do and intended",
        "Can do but not intended as RTDL's role",
        "Cannot do yet",
        "RTDL is not a DBMS",
    ],
    "docs/quick_tutorial.md": [
        "input -> traverse -> refine -> emit",
        "not a promise that every backend is always 10x faster",
        "Feature Quickstart Cookbook",
    ],
    "docs/tutorials/feature_quickstart_cookbook.md": [
        "one compact recipe per current public feature",
        "PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py",
        "The cookbook teaches feature shape through `cpu_python_reference`",
    ],
    "docs/README.md": [
        "Evaluate RTDL In Ten Minutes",
        "authoring-burden reduction",
    ],
}


def markdown_links(text: str) -> list[str]:
    links: list[str] = []
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if "://" in target:
            continue
        links.append(target.split("#", 1)[0])
    return links


def check_links() -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for rel in PUBLIC_DOCS:
        path = ROOT / rel
        if not path.exists():
            failures.append({"file": rel, "target": rel, "reason": "public doc missing"})
            continue
        text = path.read_text(encoding="utf-8")
        for target in markdown_links(text):
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                failures.append({"file": rel, "target": target, "reason": "link escapes repo"})
                continue
            if not resolved.exists():
                failures.append({"file": rel, "target": target, "reason": "missing target"})
    return failures


def check_phrases() -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                failures.append({"file": rel, "phrase": phrase, "reason": "missing phrase"})
    return failures


def run_command(entry: dict[str, object]) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    proc = subprocess.run(
        entry["cmd"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    return {
        "name": entry["name"],
        "cmd": entry["cmd"],
        "returncode": proc.returncode,
        "stdout_head": proc.stdout[:1200],
        "stderr_head": proc.stderr[:1200],
        "ok": proc.returncode == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    command_results = [run_command(entry) for entry in SMOKE_COMMANDS]
    result = {
        "goal": 497,
        "public_docs": PUBLIC_DOCS,
        "link_failures": check_links(),
        "phrase_failures": check_phrases(),
        "command_results": command_results,
    }
    result["valid"] = (
        not result["link_failures"]
        and not result["phrase_failures"]
        and all(item["ok"] for item in command_results)
    )

    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
