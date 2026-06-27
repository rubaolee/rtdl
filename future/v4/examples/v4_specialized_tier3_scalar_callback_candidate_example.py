from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4 import plan_v4_goal4698_specialized_tier3_compile


SAMPLE_PTX = """
.common .global .align 8 .u64 _ZN08NumbaEnv33custom_scalar_reduceB2v1B96;
.visible .func custom_scalar_reduce_weighted_sum(){ret;}
"""


def build_candidate_plan() -> dict[str, object]:
    plan = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        callback_symbol="custom_scalar_reduce_weighted_sum",
        callback_ptx=SAMPLE_PTX,
        toolchain_fingerprint="example-toolchain-fingerprint",
    ).as_dict()
    return {
        "status": "bounded_candidate_example_not_public_api",
        "compile_stage": plan["stage"],
        "internal_compile_allowed": plan["internal_compile_allowed"],
        "tier3_public_support_authorized": plan["tier3_public_support_authorized"],
        "release_authorized": plan["release_authorized"],
        "performance_claim_authorized": plan["performance_claim_authorized"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded V4 specialized Tier-3 scalar callback candidate example.")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    payload = build_candidate_plan()
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["compile_stage"] == "compile_cache_ready_not_executed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
