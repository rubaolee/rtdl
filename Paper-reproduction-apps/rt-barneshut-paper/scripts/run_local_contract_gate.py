#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "Paper-reproduction-apps" / "rt-barneshut-paper"
RUN_DIR = APP_DIR / "_runs" / "local_contract_gate"
COMPARE_SCRIPT = APP_DIR / "scripts" / "compare_author_contract_to_rtdl_reference.py"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_probe(name: str, args: list[str], output: Path, expected_matched: bool) -> dict[str, Any]:
    command = [sys.executable, str(COMPARE_SCRIPT), *args, "--output", str(output)]
    proc = subprocess.run(
        command,
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    payload = read_json(output) if output.exists() else {}
    observed_matched = bool(payload.get("matched"))
    passed = observed_matched == expected_matched
    return {
        "name": name,
        "status": "passed" if passed else "failed",
        "expected_matched": expected_matched,
        "observed_matched": observed_matched,
        "returncode": proc.returncode,
        "command": command,
        "output": str(output),
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
        "body_count": payload.get("body_count"),
        "rtdl_contract_mode": payload.get("rtdl_contract_mode"),
        "max_abs_error": payload.get("max_abs_error"),
        "max_rel_error": payload.get("max_rel_error"),
        "mismatch_count": payload.get("mismatch_count"),
        "claim_boundary": payload.get("claim_boundary"),
    }


def build_gate() -> tuple[dict[str, Any], int]:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    probes = [
        run_probe(
            "single_bucket_current_tree_matches",
            ["--synthetic-count", "8"],
            RUN_DIR / "single_bucket_current_tree.json",
            True,
        ),
        run_probe(
            "multi_bucket_current_tree_exposes_gap",
            ["--synthetic-count", "64"],
            RUN_DIR / "multi_bucket_current_tree_gap.json",
            False,
        ),
        run_probe(
            "multi_bucket_author_prepared_arrays_matches",
            ["--synthetic-count", "64", "--rtdl-contract", "author-prepared-arrays"],
            RUN_DIR / "multi_bucket_author_prepared_arrays.json",
            True,
        ),
    ]
    passed = all(probe["status"] == "passed" for probe in probes)
    summary = {
        "mode": "rt_barneshut_local_contract_gate",
        "status": "passed" if passed else "failed",
        "paper_reproduction_complete": False,
        "probes": probes,
        "claim_boundary": (
            "Local CPU contract gate only. It verifies force-law scaling, "
            "author-sorted output order, expected historical RTDL tree-contract "
            "gap detection, and app-layer author-prepared aggregate-array "
            "alignment. The patched author binary POD comparator remains required."
        ),
    }
    return summary, 0 if passed else 2


def main() -> int:
    summary, exit_code = build_gate()
    output = RUN_DIR / "summary.json"
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
