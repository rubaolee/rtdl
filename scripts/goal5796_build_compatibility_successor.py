#!/usr/bin/env python3
"""Build the append-only feasible-PyOptiX successor result for Goal5796."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
EVIDENCE = HISTORY / "goal5796_home_pyoptix90_compatibility_evidence_20260823"
RESULTS = EVIDENCE / "results"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ident(path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
    }


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    direct = load(RESULTS / "DIRECT_RESULT.json")
    pyoptix = load(RESULTS / "PYOPTIX_RESULT.json")
    rtdl = load(RESULTS / "RTDL_RESULT.json")
    transaction = load(RESULTS / "TRANSACTION_RESULT.json")
    build = load(RESULTS / "BUILD_RECEIPT.json")
    if not direct["outputs"] == pyoptix["outputs"] == rtdl["outputs"]:
        raise RuntimeError("A/B/D outputs differ")
    if any(value["registered_performance_timing_count"] != 0
           for value in (direct, pyoptix, rtdl)):
        raise RuntimeError("registered timing count is not zero")
    if pyoptix["stock_current_pyoptix_9_1_claimed"]:
        raise RuntimeError("compatibility arm was relabelled as stock")

    amendment = HISTORY / "goal5796_pyoptix_optix90_compatibility_preexecution_amendment_20260823.json"
    old_result = HISTORY / "goal5796_matched_implementation_result_20260823.json"
    value = {
        "schema": "rtdl.goal5796.pyoptix90_compatibility_successor_result.v1",
        "date": "2026-08-23",
        "status": "PASS_AT_CURRENT_SOURCE_OPTIX90_COMPATIBILITY_SCOPE__STOCK91_UNEXECUTED",
        "supersedes_old_result_for_feasible_binding_comparison": True,
        "does_not_supersede_stock_9_1_nonexecution": True,
        "predecessor": ident(old_result),
        "preexecution_amendment": ident(amendment),
        "gates": {
            "original_stock_current_pyoptix_9_1_gate_met": False,
            "revised_current_source_optix90_compatibility_gate_met": True,
            "goal5797_compatibility_scope_entry_authorized": True,
            "goal5798_formal_timing_authorized": False,
            "single_checkpoint_A_CFR_created": False,
        },
        "same_host_transaction": {
            "machine": transaction["machine"],
            "all_three_outputs_exact_and_identical": True,
            "semantic_spec_sha256": direct["spec_sha256"],
            "expected_output_sha256": "8f10d4ff7560e5bcabf47a3989a22ab870b302c6fd418243fd56c4ae5becaadb",
            "arms": {
                "A_direct_cuda_optix": ident(RESULTS / "DIRECT_RESULT.json"),
                "B_current_source_optix90_compatibility": ident(RESULTS / "PYOPTIX_RESULT.json"),
                "D_rtdl_public": ident(RESULTS / "RTDL_RESULT.json"),
            },
            "oracles": {
                "A": ident(RESULTS / "DIRECT_ORACLE.json"),
                "B": ident(RESULTS / "PYOPTIX_ORACLE.json"),
                "D": ident(RESULTS / "RTDL_ORACLE.json"),
            },
            "transaction_receipt": ident(RESULTS / "TRANSACTION_RESULT.json"),
        },
        "pyoptix_compatibility_identity": {
            "source_commit": build["pyoptix"]["commit"],
            "source_tree": build["pyoptix"]["tree"],
            "source_working_tree_clean": build["pyoptix"]["working_tree_clean"],
            "source_edit_count": build["source_edit_count"],
            "distribution_metadata_version": build["distribution_version"],
            "actual_optix_api_version": build["optix_api_version"],
            "optix_header_commit": build["optix_headers"]["commit"],
            "build_receipt": ident(RESULTS / "BUILD_RECEIPT.json"),
            "wheel": ident(EVIDENCE / "pyoptix-9.1.0-cp312-cp312-linux_x86_64.whl"),
            "binding_module": ident(EVIDENCE / "_optix.cpython-312-x86_64-linux-gnu.so"),
            "stock_current_pyoptix_9_1_claimed": False,
        },
        "overflow_witnesses": {
            "A": direct["capacity_overflow_witness"],
            "B": pyoptix["capacity_overflow_witness"],
            "D": rtdl["capacity_overflow_witness"],
        },
        "C_owl": {
            "status": "ANALYSED_NOT_IMPLEMENTED",
            "responsibility_artifact": ident(
                HISTORY / "goal5796_source_backed_responsibility_tables_v2_20260823.json"),
            "performance_claimed": False,
        },
        "measurement": {
            "registered_performance_timing_count": 0,
            "performance_claimed": False,
            "incidental_rtdl_lifecycle_seconds_eligible_for_comparison": False,
            "cross_version_performance_claim_allowed": False,
        },
        "claim_ceiling": {
            "pyoptix_host_binding_and_responsibility_comparison": True,
            "two_designed_matched_case_studies": True,
            "stock_current_pyoptix_9_1_execution": False,
            "performance": False,
            "usability_or_productivity": False,
            "unseen_application_generalization": False,
            "arbitrary_callback_support": False,
        },
        "remaining_goal5797_obligation": (
            "For each of five proposed RTDL mechanisms, demonstrate both mutation-liveness "
            "and semantic necessity, including a concrete accepted-invalid OWL/direct control "
            "where the related-work claim is made."
        ),
    }
    output = HISTORY / "goal5796_pyoptix90_compatibility_successor_result_20260823.json"
    output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
