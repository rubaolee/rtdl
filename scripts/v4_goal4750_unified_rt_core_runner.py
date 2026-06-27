#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rtdsl.v4_goal4750_unified_rt_core_runner import write_dry_run_artifacts


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = (
    ROOT / "future" / "v4" / "evidence" / "v4_goal4750_unified_rt_core_runner_dry_run_2026-06-26.json"
)
DEFAULT_REPORT = ROOT / "future" / "v4" / "v4_goal4750_unified_rt_core_runner_dry_run_2026-06-26.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Write V4 Goal4750 unified runner dry-run artifacts.")
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    payload = write_dry_run_artifacts(evidence_path=args.evidence, report_path=args.report)
    print(args.evidence)
    print(args.report)
    print(payload["validation"]["status"])
    return 0 if payload["validation"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
