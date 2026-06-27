from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4698_specialized_tier3_compile_cache import validate_v4_goal4698_specialized_tier3_compile_cache


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    accepted = payload["accepted_plan"]
    rejected = payload["rejected_plan"]
    incomplete = payload["incomplete_plan"]
    failure = payload["compile_failure_classification"]
    lines = [
        "# V4 Goal4698 Specialized Tier-3 Compile/Cache Scaffold",
        "",
        "Status: compile/cache/error-reporting scaffold, not public Tier-3 support",
        "",
        f"- validation: `{payload['validation_status']}`",
        f"- goal status: `{payload['goal_status']}`",
        f"- next goal: `{payload['next_goal']}`",
        "",
        "## Accepted Compile-Ready Plan",
        "",
        f"- stage: `{accepted['stage']}`",
        f"- cache key: `{accepted['cache_key']}`",
        f"- internal compile allowed: `{accepted['internal_compile_allowed']}`",
        "",
        "## Rejection / Error Behavior",
        "",
        f"- rejected stage: `{rejected['stage']}`",
        f"- rejected error: `{rejected['error_code']}`",
        f"- incomplete stage: `{incomplete['stage']}`",
        f"- incomplete error: `{incomplete['error_code']}`",
        f"- compile failure classification: `{failure['error_code']}`",
        "",
        "## Boundary",
        "",
        "This scaffold creates deterministic cache/error behavior for internal productization only. It is not public Tier-3 support, not raw OptiX callback support, not release authorization, and not a performance claim.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Record V4 Goal4698 specialized Tier-3 compile/cache scaffold.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    validation = validate_v4_goal4698_specialized_tier3_compile_cache()
    payload = {"schema": "rtdl.v4.goal4698_specialized_tier3_compile_cache.v1", "validation_status": validation["status"], **validation}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if validation["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
