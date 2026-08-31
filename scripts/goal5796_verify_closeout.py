#!/usr/bin/env python3
"""Independently verify the frozen Goal5796 closeout without importing GPU arms."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
EVIDENCE = HISTORY / "goal5796_matched_functional_evidence_v2_20260823"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_identity(value: dict[str, object]) -> None:
    path = ROOT / str(value["path"])
    require(path.is_file(), f"missing identity path: {path}")
    require(path.stat().st_size == value["bytes"], f"size mismatch: {path}")
    require(sha256(path) == value["sha256"], f"hash mismatch: {path}")


def main() -> None:
    spec_path = ROOT / "experiments" / "goal5796_matched" / "semantic_spec.json"
    oracle_path = ROOT / "experiments" / "goal5796_matched" / "independent_oracle.py"
    module_spec = importlib.util.spec_from_file_location("goal5796_audit_oracle", oracle_path)
    require(module_spec is not None and module_spec.loader is not None, "oracle loader absent")
    oracle = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(oracle)
    expected = oracle.build_expected(load(spec_path))
    require(
        oracle.digest(expected) == "8f10d4ff7560e5bcabf47a3989a22ab870b302c6fd418243fd56c4ae5becaadb",
        "independent expected-output digest mismatch",
    )

    direct = load(EVIDENCE / "DIRECT_RESULT.json")
    rtdl = load(EVIDENCE / "RTDL_RESULT.json")
    require(direct["outputs"] == expected, "direct output differs from independent oracle")
    require(rtdl["outputs"] == expected, "RTDL output differs from independent oracle")
    for arm, value in (("direct", direct), ("rtdl", rtdl)):
        witness = value["capacity_overflow_witness"]
        require(witness["status"] == "FAIL_CLOSED", f"{arm} overflow did not fail closed")
        require(not witness["application_result_exposed"], f"{arm} exposed a partial result")
        require(witness["capacity"] == 7, f"{arm} capacity changed")
        require(witness["expected_unique_row_count"] == 8, f"{arm} witness changed")

    result_path = HISTORY / "goal5796_matched_implementation_result_20260823.json"
    result = load(result_path)
    require(not result["goal5796_completion_gate_met"], "missing B was relabelled complete")
    require(result["arm_results"]["A_direct_cuda_optix"]["status"] == "PASS", "A not PASS")
    require(result["arm_results"]["D_rtdl_public"]["status"] == "PASS", "D not PASS")
    b = result["arm_results"]["B_current_pyoptix"]
    for key in (
        "correctness_result_exists",
        "package_install_attempted",
        "optix_context_created",
        "substitution_used",
    ):
        require(b[key] is False, f"B gate {key} is not false")
    require(
        result["arm_results"]["C_owl"]["status"] == "ANALYSED_NOT_IMPLEMENTED",
        "C status changed",
    )
    require(result["measurement"]["registered_performance_timing_count"] == 0, "timing count nonzero")
    require(not result["measurement"]["performance_claimed"], "performance claimed")
    require(not result["next_gate"]["goal5797_full_entry_authorized"], "Goal5797 incorrectly authorized")
    require(not result["next_gate"]["goal5798_formal_timing_authorized"], "Goal5798 incorrectly authorized")

    identities: list[dict[str, object]] = []
    for arm in ("A_direct_cuda_optix", "D_rtdl_public"):
        for value in result["arm_results"][arm].values():
            if isinstance(value, dict) and {"path", "bytes", "sha256"} <= set(value):
                identities.append(value)
    identities.extend(
        [
            result["s0"],
            result["responsibility_tables"]["artifact"],
            result["verification"]["environment_receipt"],
            result["closeout_documents"]["technical_report"],
            result["closeout_documents"]["strict_self_review"],
        ]
    )
    for value in identities:
        verify_identity(value)

    receipt = {
        "schema": "rtdl.goal5796.independent_closeout_verification.v1",
        "status": "PASS",
        "spec_sha256": sha256(spec_path),
        "expected_output_sha256": oracle.digest(expected),
        "direct_output_exact": True,
        "rtdl_output_exact": True,
        "both_overflow_witnesses_fail_closed_without_result": True,
        "verified_identity_count": len(identities),
        "missing_pyoptix_denominator_preserved": True,
        "registered_performance_timing_count": 0,
        "goal5796_completion_gate_met": False,
        "goal5798_formal_timing_authorized": False,
        "result_sha256": sha256(result_path),
    }
    output = HISTORY / "goal5796_closeout_independent_verification_20260823.json"
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
