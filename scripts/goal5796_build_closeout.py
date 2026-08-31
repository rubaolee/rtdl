#!/usr/bin/env python3
"""Build the append-only Goal5794 S0 and Goal5796 closeout records.

This builder deliberately records an unmet execution gate instead of converting
source inspection or a legacy OptiX run into a current-PyOptiX result.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
EVIDENCE = HISTORY / "goal5796_matched_functional_evidence_v2_20260823"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(relative: str) -> dict[str, object]:
    path = ROOT / relative
    return {
        "path": relative.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    spec = identity("experiments/goal5796_matched/semantic_spec.json")
    oracle = identity("experiments/goal5796_matched/independent_oracle.py")
    direct_source = identity("experiments/goal5796_matched/direct_optix.cpp")
    direct_build = identity("experiments/goal5796_matched/build_direct.sh")
    device_source = identity("experiments/goal5796_matched/matched_device.cu")
    pyoptix_source = identity("experiments/goal5796_matched/pyoptix_baseline.py")
    rtdl_source = identity("experiments/goal5796_matched/rtdl_baseline.py")
    environment_path = HISTORY / "goal5796_linux_functional_environment_and_current_pyoptix_gate_20260823.json"
    responsibility_path = HISTORY / "goal5796_source_backed_responsibility_tables_v2_20260823.json"
    environment = load_json(environment_path)
    responsibility = load_json(responsibility_path)
    direct_result = load_json(EVIDENCE / "DIRECT_RESULT.json")
    rtdl_result = load_json(EVIDENCE / "RTDL_RESULT.json")

    s0 = {
        "schema": "rtdl.goal5794.matched_baseline_s0.v1",
        "date": "2026-08-23",
        "status": "S0_FROZEN__SOURCE_AND_EXPERIMENT_CONTRACT_ONLY",
        "controlling_plan": identity(
            "history/internal_docs/goal5794_to_goal5799_cgo_execution_plan_v2_owl_aware_20260823.md"
        ),
        "upstream_pins": {
            "pyoptix": {
                "repository": "https://github.com/NVIDIA/otk-pyoptix",
                "repository_commit": "3144f224c0fd18733925faf3d8fb82c7376b8dcf",
                "repository_tree": "0bf0ec24efb4a43f129aee25dd265aa8149374e3",
                "repository_tag": "v1.3.0",
                "python_distribution_version": "9.1.0",
                "pypi_sdist_bytes": 8933523,
                "pypi_sdist_sha256": "224f7fa2993240a67cd36cebe386e3c1be4a57f3bb5ace4c8532587950abacdc",
                "optix_header_commit": "f1f6dd803f3159992d248178f6e09421c6eb8b6d",
                "normal_custom_intersection_path": "python_host_plus_cuda_cpp_device_via_nvrtc",
            },
            "owl": {
                "repository": "https://github.com/NVIDIA/OWL",
                "repository_commit": "df7390b16bce5244b7352ca6d3e320f838297072",
                "repository_tree": "c31d2b76056417b2387fae6cf584b7fa3c5688b9",
                "execution_status": "ANALYSED_NOT_IMPLEMENTED",
            },
        },
        "frozen_semantics": spec,
        "independent_oracle": {
            **oracle,
            "imports_gpu_arms": False,
            "expected_output_sha256": "8f10d4ff7560e5bcabf47a3989a22ab870b302c6fd418243fd56c4ae5becaadb",
        },
        "arms": {
            "A_direct_cuda_optix": {
                "required": True,
                "source": direct_source,
                "build": direct_build,
                "device_program_embedded_in_host_source": True,
            },
            "B_current_pyoptix": {
                "required": True,
                "source": pyoptix_source,
                "device_source": device_source,
                "legacy_or_mock_substitution_allowed": False,
                "source_inspection_may_replace_execution": False,
            },
            "C_owl": {
                "required_for_responsibility": True,
                "execution_required": False,
                "status": "ANALYSED_NOT_IMPLEMENTED",
                "performance_claim_allowed": False,
            },
            "D_rtdl_public": {
                "required": True,
                "source": rtdl_source,
                "public_import_only_required": True,
            },
        },
        "equality_requirements": [
            "same semantic_spec bytes",
            "same binary32 inputs and closed-boundary predicate",
            "same custom-AABB item/query identities and canonical ordering",
            "same built-in-triangle per-ray counts and weighted-u64 reduction",
            "same capacity-7 overflow witness with no partial application result",
            "independent CPU oracle does not import A/B/C/D",
        ],
        "run_policy": {
            "correctness_before_performance": True,
            "registered_performance_timing_count": 0,
            "incidental_lifecycle_durations_are_performance_evidence": False,
            "same_machine_performance_comparison_authorized": False,
            "formal_timing_authorized": False,
        },
        "claim_ceiling": [
            "two designed matched non-rendering case studies",
            "functional correctness only for arms actually executed",
            "no unseen-application generalization inference",
            "no usability or productivity inference",
            "no performance inference",
        ],
    }

    result = {
        "schema": "rtdl.goal5796.matched_implementation_closeout.v1",
        "date": "2026-08-23",
        "status": "TERMINAL_PARTIAL__A_AND_D_EXACT__C_ANALYSED_ONLY__B_ENVIRONMENT_BLOCKED",
        "goal5796_completion_gate_met": False,
        "reason_gate_not_met": (
            "The mandatory current PyOptiX 9.1 arm cannot execute on the designated "
            "R580 host because OptiX 9.1 requires R590 or later. No substitute was used."
        ),
        "s0": {
            "path": "history/internal_docs/goal5794_s0_matched_baseline_contract_20260823.json",
        },
        "semantic_spec": spec,
        "oracle": oracle,
        "arm_results": {
            "A_direct_cuda_optix": {
                "status": direct_result["status"],
                "all_registered_outputs_exact": True,
                "capacity_overflow_fail_closed": direct_result["capacity_overflow_witness"],
                "result": identity(
                    "history/internal_docs/goal5796_matched_functional_evidence_v2_20260823/DIRECT_RESULT.json"
                ),
                "oracle_receipt": identity(
                    "history/internal_docs/goal5796_matched_functional_evidence_v2_20260823/DIRECT_ORACLE.json"
                ),
                "executable": identity(
                    "history/internal_docs/goal5796_matched_functional_evidence_v2_20260823/direct_optix"
                ),
            },
            "B_current_pyoptix": {
                "status": environment["current_pyoptix_gate"]["status"],
                "implementation_source_complete": True,
                "source_static_checks_passed": True,
                "package_install_attempted": environment["current_pyoptix_gate"]["package_install_attempted"],
                "optix_context_created": environment["current_pyoptix_gate"]["optix_context_created"],
                "substitution_used": environment["current_pyoptix_gate"]["substitution_used"],
                "correctness_result_exists": False,
                "source": pyoptix_source,
            },
            "C_owl": {
                "status": "ANALYSED_NOT_IMPLEMENTED",
                "source_backed_responsibility_rows_exist": True,
                "correctness_result_exists": False,
                "performance_result_exists": False,
            },
            "D_rtdl_public": {
                "status": rtdl_result["status"],
                "all_registered_outputs_exact": True,
                "public_import_only": rtdl_result["public_import_only"],
                "capacity_overflow_fail_closed": rtdl_result["capacity_overflow_witness"],
                "result": identity(
                    "history/internal_docs/goal5796_matched_functional_evidence_v2_20260823/RTDL_RESULT.json"
                ),
                "oracle_receipt": identity(
                    "history/internal_docs/goal5796_matched_functional_evidence_v2_20260823/RTDL_ORACLE.json"
                ),
                "loaded_native": identity(
                    "history/internal_docs/goal5796_matched_functional_evidence_v2_20260823/librtdl_optix.so"
                ),
            },
        },
        "product_defect_and_repair": {
            "defect": (
                "The public semantic result capacity was incorrectly reused as the private "
                "raw traversal-event capacity, so duplicate any-hit events could cause false overflow."
            ),
            "repair": (
                "The native v2 ABI privately provisions enough raw-event space, canonicalizes and "
                "deduplicates before applying the public semantic capacity, and exposes both raw and "
                "unique counts for diagnosis."
            ),
            "repaired_sources": [
                identity("src/native/optix/rtdl_optix_api.cpp"),
                identity("src/native/optix/rtdl_optix_v4_callback_poc.cpp"),
                identity("src/rtdsl/v4_bounded_relation_prepared_runtime.py"),
            ],
            "evidence": {
                "diagnostic_cross_raw_unique": [4, 2],
                "broad_raw_unique": [16, 8],
                "capacity_7_expected_unique_8": "FAIL_CLOSED_NO_RESULT",
            },
        },
        "responsibility_tables": {
            "artifact": {
                "path": str(responsibility_path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": responsibility_path.stat().st_size,
                "sha256": sha256(responsibility_path),
            },
            "composition_rows": len(responsibility["composition_ownership"]),
            "protocol_rows": len(responsibility["protocol_contract_ownership"]),
            "device_language_rows": len(responsibility["device_language_path"]),
            "historical_application_rows": len(responsibility["historical_application_table"]),
            "raydb_private_loader_exception_explicit": True,
            "owl_composition_counted_as_rtdl_novelty": False,
        },
        "verification": {
            "local_unittest_count": 37,
            "local_unittest_status": "PASS",
            "linux_host": "lestat@192.168.1.20",
            "wsl_used": False,
            "A_and_D_executed_on_same_host": True,
            "environment_receipt": {
                "path": str(environment_path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": environment_path.stat().st_size,
                "sha256": sha256(environment_path),
            },
        },
        "measurement": {
            "registered_performance_timing_count": 0,
            "performance_claimed": False,
            "incidental_public_lifecycle_seconds_present": True,
            "incidental_public_lifecycle_seconds_eligible_for_comparison": False,
        },
        "limitations": [
            "No current PyOptiX execution or correctness receipt exists.",
            "OWL is source-backed analysed-only, not an executable arm.",
            "The two tasks are author-designed matched case studies, not unseen-user generalization exams.",
            "There is no third-party user, usability study, or functionally matched performance result.",
            "GTX1070 functional evidence is not modern-RTX evidence.",
            "The duplicate-event capacity repair is proved only for the bounded family implemented here.",
        ],
        "next_gate": {
            "minimum_external_resource": "one R590+ non-WSL NVIDIA host compatible with current PyOptiX 9.1",
            "allowed_action": "execute the already-frozen B arm non-timed and re-run A/D correctness on that same host",
            "forbidden_substitutions": [
                "legacy PyOptiX",
                "OptiX 9.0 relabelled as 9.1",
                "mock PyOptiX",
                "source inspection relabelled as execution",
                "old V2/V4 measurements",
            ],
            "goal5797_full_entry_authorized": False,
            "goal5798_formal_timing_authorized": False,
        },
        "closeout_documents": {
            "technical_report": identity(
                "history/internal_docs/goal5796_matched_implementation_technical_report_20260823.md"
            ),
            "strict_self_review": identity(
                "history/internal_docs/self_review_goal5796_matched_implementation_20260823.md"
            ),
            "external_cfr_created": False,
            "external_cfr_policy": "defer_to_single_checkpoint_A_CFR_after_Goal5797",
        },
    }

    s0_path = HISTORY / "goal5794_s0_matched_baseline_contract_20260823.json"
    write_json(s0_path, s0)
    result["s0"].update({"bytes": s0_path.stat().st_size, "sha256": sha256(s0_path)})
    write_json(HISTORY / "goal5796_matched_implementation_result_20260823.json", result)


if __name__ == "__main__":
    main()
