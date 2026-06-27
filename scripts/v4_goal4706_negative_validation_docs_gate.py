from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4706_negative_validation_docs_gate import validate_v4_goal4706_negative_validation_docs_gate


EXAMPLE = ROOT / "future" / "v4" / "examples" / "v4_specialized_tier3_scalar_callback_candidate_example.py"


def _run_example() -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, str(EXAMPLE)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    payload = json.loads(proc.stdout) if proc.returncode == 0 and proc.stdout.strip() else None
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[:4000],
        "stderr": proc.stderr.strip()[:4000],
        "payload": payload,
    }


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    gate = payload["gate"]
    example = payload["example_run"]
    lines = [
        "# V4 Goal4706 Negative Validation And Example Gate",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- status: `{gate['status']}`",
        f"- accepted example status: `{gate['accepted_example_status']}`",
        f"- example returncode: `{example['returncode']}`",
        "",
        "## Negative Rows",
        "",
        "| case | stage | error code | compile allowed |",
        "|---|---|---|---|",
    ]
    for row in gate["negative_rows"]:
        lines.append(
            f"| `{row['case_id']}` | `{row['stage']}` | `{row['error_code']}` | `{row['internal_compile_allowed']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate validates fail-closed behavior and a bounded candidate example only. It does not authorize public Tier-3 support, release wording, or performance claims.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V4 Goal4706 negative validation/docs gate evidence.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4706_negative_validation_docs_gate()
    example_run = _run_example()
    payload = {
        "schema": "rtdl.v4.goal4706_negative_validation_docs_gate.v1",
        "validation_status": validation["status"],
        **validation,
        "example_run": example_run,
    }
    if example_run["returncode"] != 0:
        payload["validation_status"] = "failed"
        payload["status"] = "failed"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
