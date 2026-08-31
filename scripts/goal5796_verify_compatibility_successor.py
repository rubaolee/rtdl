#!/usr/bin/env python3
"""Independent local verifier for the Goal5796 compatibility successor."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
EVIDENCE = HISTORY / "goal5796_home_pyoptix90_compatibility_evidence_20260823"
RESULTS = EVIDENCE / "results"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_identity(value: dict[str, object]) -> None:
    path = ROOT / str(value["path"])
    require(path.is_file(), f"missing {path}")
    require(path.stat().st_size == value["bytes"], f"size mismatch {path}")
    require(sha(path) == value["sha256"], f"hash mismatch {path}")


def main() -> None:
    oracle_path = ROOT / "experiments/goal5796_matched/independent_oracle.py"
    spec_path = ROOT / "experiments/goal5796_matched/semantic_spec.json"
    module_spec = importlib.util.spec_from_file_location("goal5796_successor_oracle", oracle_path)
    require(module_spec is not None and module_spec.loader is not None, "oracle loader absent")
    oracle = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(oracle)
    expected = oracle.build_expected(load(spec_path))
    require(
        oracle.digest(expected) == "8f10d4ff7560e5bcabf47a3989a22ab870b302c6fd418243fd56c4ae5becaadb",
        "oracle digest mismatch")

    names = ("DIRECT_RESULT.json", "PYOPTIX_RESULT.json", "RTDL_RESULT.json")
    arm_values = {name: load(RESULTS / name) for name in names}
    for name, value in arm_values.items():
        require(value["outputs"] == expected, f"{name} differs from oracle")
        require(value["registered_performance_timing_count"] == 0, f"{name} timing nonzero")
        witness = value["capacity_overflow_witness"]
        require(witness["status"] == "FAIL_CLOSED", f"{name} overflow accepted")
        require(not witness["application_result_exposed"], f"{name} exposed partial output")
    b = arm_values["PYOPTIX_RESULT.json"]
    require(b["arm"] == "B_CURRENT_PYOPTIX_SOURCE_OPTIX90_COMPATIBILITY", "B label drift")
    require(b["pyoptix_distribution_version"] == "9.1.0", "distribution drift")
    require(b["optix_api_version"] == "9.0.0", "OptiX API drift")
    require(not b["stock_current_pyoptix_9_1_claimed"], "stock relabel")

    successor_path = HISTORY / "goal5796_pyoptix90_compatibility_successor_result_20260823.json"
    successor = load(successor_path)
    require(successor["gates"]["revised_current_source_optix90_compatibility_gate_met"], "gate false")
    require(not successor["gates"]["original_stock_current_pyoptix_9_1_gate_met"], "stock gate true")
    require(successor["gates"]["goal5797_compatibility_scope_entry_authorized"], "Goal5797 closed")
    require(not successor["gates"]["goal5798_formal_timing_authorized"], "Goal5798 opened")

    identities: list[dict[str, object]] = [
        successor["predecessor"], successor["preexecution_amendment"],
        successor["same_host_transaction"]["transaction_receipt"],
        successor["pyoptix_compatibility_identity"]["build_receipt"],
        successor["pyoptix_compatibility_identity"]["wheel"],
        successor["pyoptix_compatibility_identity"]["binding_module"],
        successor["C_owl"]["responsibility_artifact"],
    ]
    identities.extend(successor["same_host_transaction"]["arms"].values())
    identities.extend(successor["same_host_transaction"]["oracles"].values())
    for value in identities:
        verify_identity(value)

    receipt = {
        "schema": "rtdl.goal5796.pyoptix90_compatibility_independent_verification.v1",
        "status": "PASS",
        "expected_output_sha256": oracle.digest(expected),
        "A_B_D_exact": True,
        "overflow_fail_closed_no_partial_result": True,
        "verified_identity_count": len(identities),
        "stock_9_1_relabel_absent": True,
        "revised_goal5796_gate_met": True,
        "goal5797_compatibility_scope_entry_authorized": True,
        "goal5798_formal_timing_authorized": False,
        "registered_performance_timing_count": 0,
        "successor_result_sha256": sha(successor_path),
    }
    output = HISTORY / "goal5796_pyoptix90_compatibility_independent_verification_20260823.json"
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
