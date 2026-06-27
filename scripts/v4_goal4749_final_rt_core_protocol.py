#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rtdsl.v4_goal4749_final_rt_core_protocol import write_protocol_artifacts


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = (
    ROOT / "future" / "v4" / "evidence" / "v4_goal4749_final_rt_core_protocol_2026-06-26.json"
)
DEFAULT_REPORT = ROOT / "future" / "v4" / "v4_goal4749_final_rt_core_protocol_2026-06-26.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Write the V4 Goal4749 final RT-core app protocol.")
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    payload = write_protocol_artifacts(evidence_path=args.evidence, report_path=args.report)
    print(args.evidence)
    print(args.report)
    print(payload["validation"]["status"])
    return 0 if payload["validation"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
