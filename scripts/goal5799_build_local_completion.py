#!/usr/bin/env python3
"""Build Goal5799's review absorption, evidence freeze, and sole review CFR.

This transaction is deliberately local, offline, and non-measuring.  It reads
already-frozen Goal5797/5798/5799 evidence, binds the exact Goal5793 exposure
registry, and turns the returned review into executable constraints for later
Goals 5800--5802.  It does not execute an application, contact a provider,
open an SSH/POD session, or authorize Goal5802/5803.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import tarfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"

PLAN_CFR = HISTORY / "call_for_review_goal5799_cgo_contribution_performance_repair_generalization_and_usability_plan_20260824.md"
RETURNED_REVIEW = HISTORY / "review_goal5799_cgo_contribution_performance_repair_generalization_and_usability_plan_20260824.md"
A1_CFR = HISTORY / "call_for_review_goal5797_a1_postreview_leaf_oracle_and_provenance_closure_20260823.md"
A1_RESULT = HISTORY / "goal5797_a1_exhaustive_populated_leaf_liveness_result_20260823.json"
X3_JOURNAL = HISTORY / "goal5793_x3_provider_search_journal_20260822.jsonl"
X3_CLOSURE = HISTORY / "goal5793_x3_terminal_owner_closure_and_a1_entry_20260823.json"
X3_REGISTRY = HISTORY / "goal5793_x3_a1_observed_work_exposure_registry_20260824.json"
X3_REGISTRY_VERIFICATION = HISTORY / "goal5793_x3_a1_observed_work_exposure_registry_independent_verification_20260824.json"
V11_EVIDENCE = HISTORY / "goal5798_v11_rtx4000ada_formal_evidence_20260824.tar.gz"
V11_CANDIDATE = HISTORY / "goal5798_portable_pod_candidate_v11_20260824.tar.gz"

ABSORPTION = HISTORY / "goal5799_external_review_absorption_and_execution_freeze_20260824.json"
PHASE_LEDGER = HISTORY / "goal5799_v11_cold_phase_ledger_20260824.json"
CONTRACT = HISTORY / "goal5799_performance_and_evidence_contract_20260824.json"
RESULT = HISTORY / "goal5799_local_completion_result_20260824.json"
SELF_REVIEW = HISTORY / "self_review_goal5799_local_completion_20260824.md"
CFR = HISTORY / "call_for_review_goal5799_local_completion_and_goal5800_5801_entry_20260824.md"

PINNED_INPUTS: dict[Path, tuple[int, str]] = {
    PLAN_CFR: (41_683, "fa8220420080fe0ccca63a99da206a53ccbe0f38c53f5218ba517d9bdd1d809b"),
    RETURNED_REVIEW: (39_418, "bb889cd8e08c74beab93cb1d3592d8f28f203e80150c83e8eb281d541dbf9f01"),
    A1_CFR: (265_655, "e0f15fb1b599e2ac18dbb44c1142eb23efd2816bbc457715b5c72bb8233903e9"),
    A1_RESULT: (52_151, "4d200a198ab42291d562e9f0861badbd623cb8a36c2ef81c1c3b86fc887278a1"),
    X3_JOURNAL: (9_326_661, "94ab0fc951c728569c0d57f649de918feeb547a8f4dac0ea48ec43f176b7e4c5"),
    X3_CLOSURE: (3_640, "25e3f28e730b5ef119c9aac2ba2fda10b9358a8b0a2844ea4372b9cb0bcf606a"),
    X3_REGISTRY: (177_701, "39434a34f0215158c4e83f92c7500c79c4cc3083af9be129d9557591f336196f"),
    X3_REGISTRY_VERIFICATION: (1_234, "b59f80f55f78c61a2990dcca7b1f2c78583dfed711300e59c8df70a78bba75c7"),
    V11_EVIDENCE: (13_668_025, "05070ddc86a8e971a046fe4affb92be1cae65087438335db57fd84c81cfda11b"),
    V11_CANDIDATE: (2_183_480, "92cca9ca67ecc15ffb26c2c15440991a8aeebcf87a033483041c05e23a2dd877"),
}

OUTPUTS = (ABSORPTION, PHASE_LEDGER, CONTRACT, RESULT, SELF_REVIEW, CFR)
DOMAIN_PREFIX = "rtdl.goal5799.local_completion"


class Goal5799Error(ValueError):
    """Stable fail-closed Goal5799 error."""


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(payload),
        "sha256": sha(payload),
    }


def verify_pinned_inputs() -> None:
    for path, (expected_bytes, expected_sha) in PINNED_INPUTS.items():
        if not path.is_file() or path.is_symlink():
            raise Goal5799Error(f"PINNED_INPUT_NOT_REGULAR:{path.name}")
        payload = path.read_bytes()
        if len(payload) != expected_bytes or sha(payload) != expected_sha:
            raise Goal5799Error(f"PINNED_INPUT_IDENTITY_MISMATCH:{path.name}")


def _sealed(document: dict[str, Any], name: str) -> dict[str, Any]:
    field = f"{name}_sha256"
    document[field] = ""
    document[field] = seal_document(
        document,
        seal_field=field,
        domain=f"{DOMAIN_PREFIX}.{name}.v1",
        version=1,
    )
    return document


def build_absorption() -> dict[str, Any]:
    registry = json.loads(X3_REGISTRY.read_text(encoding="utf-8", errors="strict"))
    a1 = json.loads(A1_RESULT.read_text(encoding="utf-8", errors="strict"))
    if registry.get("counts") != {
        "arxiv_rows": 0,
        "doi_rows": 195,
        "fallback_rows": 199,
        "fallback_unavailable_rows": 1,
        "observed_rows": 200,
        "openalex_rows": 200,
        "selection_eligible_rows": 0,
        "unique_canonical_work_identities": 200,
        "unique_openalex_ids": 200,
    }:
        raise Goal5799Error("EXPOSURE_REGISTRY_COUNTS_MISMATCH")
    required_a1 = {
        "populated_leaf_count": 19,
        "pre_registered_leaf_count": 19,
        "decision_bearing_count": 19,
        "projection_bytes_unchanged_count": 19,
        "single_expected_finding_count": 19,
        "non_decision_bearing_count": 0,
    }
    for key, value in required_a1.items():
        if a1.get(key) != value:
            raise Goal5799Error(f"A1_SUMMARY_MISMATCH:{key}")
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.external_review_absorption_and_execution_freeze.v1",
        "date": "2026-08-24",
        "status": "PASS__RETURNED_REVIEW_FULLY_ABSORBED__LOCAL_GOAL5799_COMPLETEABLE",
        "review": identity(RETURNED_REVIEW),
        "reviewed_plan": identity(PLAN_CFR),
        "verdict": {
            "label": "APPROVE_WITH_CONDITIONS",
            "P0": 0,
            "P1": 4,
            "P2": 4,
            "P3": 2,
        },
        "owner_directives_in_active_record": [
            "我同意更新后的GOALS。现在我们需要更好的实现它们。顺序如何？并行机会在哪？",
            "完成Goal5799 ！不要降智，有问题翻看历史记录；给我提要求必须你首先防愚蠢三问！",
        ],
        "anti_stupidity_three_questions_before_owner_request": [
            "Can the immutable/local project history answer it?",
            "Can bounded machine inspection or a safe local experiment answer it?",
            "Can a conservative assumption preserve intent without expanding authority?",
        ],
        "p1_absorption": {
            "P1_1_tautological_timing_gates": {
                "status": "CLOSED_IN_GOAL5799_FREEZE_FOR_FUTURE_DESIGN",
                "action": "ON/bypass becomes structural identity plus falsifiable cache-hit negative assertions; GPU_KERNEL becomes sanity-only; only STEADY_E2E, PREPARE, and DEPLOYMENT_COLD carry comparative gates.",
            },
            "P1_2_baseline_asymmetry": {
                "status": "CLOSED_IN_GOAL5799_FREEZE_FOR_FUTURE_DESIGN",
                "action": "Operational idiomaticity, equal timed boundaries, per-arm engineering ledger, and a pre-worker external competence question are mandatory.",
            },
            "P1_3_200_observed_works_unregistered": {
                "status": "LOCAL_REPAIR_COMPLETE__EXTERNAL_REVIEW_REQUESTED__GOAL5803_REMAINS_LOCKED",
                "registry": identity(X3_REGISTRY),
                "independent_verification": identity(X3_REGISTRY_VERIFICATION),
                "observed_rows": 200,
                "selection_eligible_rows": 0,
            },
            "P1_4_goal5803_schedule_unrealistic": {
                "status": "CLOSED_BY_DATED_DESCOPE_LADDER",
                "cutoff": "2026-08-27T23:59:59-04:00",
                "default_after_cutoff": "PLAN_PAPER_WITH_ZERO_EXTERNAL_USER_OR_NEW_APP_EVIDENCE",
                "participant_study": "DEFER_POST_SUBMISSION_WITHOUT_DELAYING_CURRENT_MANUSCRIPT",
            },
        },
        "p2_absorption": {
            "direct_pyoptix_first_class_row": True,
            "hosted_backend_maximum_claim_is_noninferiority": True,
            "build_cold_and_amortization_required": True,
            "v11_prepared_win_withdrawal_reported_positively": True,
        },
        "p3_absorption": {
            "unregistered_diagnostic_label_on_every_diagnostic_number": True,
            "artifact_anonymity_and_manuscript_anonymity_are_separate_gates": True,
        },
        "goal5797_a1": {
            "local_status": "19_OF_19_POPULATED_LEAVES_DECISION_BEARING__EXTERNAL_REVIEW_PENDING",
            "result": identity(A1_RESULT),
            "single_file_review_payload": identity(A1_CFR),
        },
        "authorization": {
            "goal5799_local_offline_completion": True,
            "goal5800_local_untimed_implementation_after_this_freeze": True,
            "goal5801_local_untimed_implementation_after_this_freeze": True,
            "goal5802_formal_measurement": False,
            "goal5803_external_evidence": False,
            "network_provider_query": False,
            "ssh_pod_gpu": False,
            "external_contact_or_participant_recruitment": False,
            "submission_claim": False,
        },
        "absorption_sha256": "",
    }
    return _sealed(document, "absorption")


def _read_cold_receipts() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with tarfile.open(V11_EVIDENCE, "r:gz") as archive:
        names = sorted(name for name in archive.getnames() if name.endswith("/final_receipt.json"))
        for name in names:
            member = archive.extractfile(name)
            if member is None:
                raise Goal5799Error(f"V11_RECEIPT_MISSING:{name}")
            receipt = json.load(member)
            if receipt.get("mode") == "COLD_FRESH_PROCESS":
                rows.append(receipt)
    if len(rows) != 144:
        raise Goal5799Error(f"V11_COLD_RECEIPT_COUNT_MISMATCH:{len(rows)}")
    return rows


def _sum_execute(value: Any) -> int:
    if not isinstance(value, list) or not value or any(type(item) is not int or item < 0 for item in value):
        raise Goal5799Error("V11_COMPLETE_EXECUTE_SCHEMA_INVALID")
    return sum(value)


def build_phase_ledger() -> dict[str, Any]:
    receipts = _read_cold_receipts()
    rows: list[dict[str, Any]] = []
    for receipt in receipts:
        durations = receipt.get("durations_ns")
        if not isinstance(durations, Mapping):
            raise Goal5799Error("V11_DURATIONS_MISSING")
        wall = durations.get("controller_process_wall_ns")
        input_ns = durations.get("input_materialization_ns")
        prepare_ns = durations.get("common_preparation_total_ns")
        close_raw = durations.get("close_ns")
        if type(wall) is not int or wall <= 0:
            raise Goal5799Error("V11_WALL_INVALID")
        if type(input_ns) is not int or input_ns < 0 or type(prepare_ns) is not int or prepare_ns < 0:
            raise Goal5799Error("V11_DIRECT_PHASE_INVALID")
        if close_raw is None:
            close_ns = 0
            close_observation = "NOT_EMITTED_BY_ARM__COUNTED_AS_ZERO_NOT_INFERRED"
        elif type(close_raw) is int and close_raw >= 0:
            close_ns = close_raw
            close_observation = "DIRECTLY_METERED"
        else:
            raise Goal5799Error("V11_CLOSE_PHASE_INVALID")
        execute_ns = _sum_execute(durations.get("complete_execute_ns"))
        directly_metered = input_ns + prepare_ns + execute_ns + close_ns
        residual = wall - directly_metered
        if residual < 0:
            raise Goal5799Error(f"V11_NEGATIVE_ENVELOPE_RESIDUAL:{receipt.get('worker_id')}")
        phases = {
            "input_materialization_ns": input_ns,
            "common_preparation_total_ns": prepare_ns,
            "complete_execute_ns": execute_ns,
            "close_ns": close_ns,
            "controller_process_envelope_residual_ns": residual,
        }
        if sum(phases.values()) != wall:
            raise Goal5799Error("V11_PHASE_SUM_MISMATCH")
        rows.append(
            {
                "worker_id": receipt.get("worker_id"),
                "task": receipt.get("task"),
                "arm": receipt.get("arm"),
                "sample_index": receipt.get("row_sample_index"),
                "wall_ns": wall,
                "phases_ns": phases,
                "close_observation": close_observation,
                "directly_metered_ns": directly_metered,
                "directly_metered_fraction": directly_metered / wall,
                "named_accounting_fraction": 1.0,
                "source_receipt_sha256": receipt.get("receipt_sha256"),
            }
        )
    counts = Counter((row["task"], row["arm"]) for row in rows)
    if set(counts.values()) != {24} or len(counts) != 6:
        raise Goal5799Error(f"V11_COLD_CELL_COUNTS_MISMATCH:{counts!r}")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["task"]), str(row["arm"]))].append(row)
    summaries = []
    for (task, arm), group in sorted(grouped.items()):
        summaries.append(
            {
                "task": task,
                "arm": arm,
                "samples": len(group),
                "median_wall_ns": statistics.median(row["wall_ns"] for row in group),
                "median_directly_metered_fraction": statistics.median(
                    row["directly_metered_fraction"] for row in group
                ),
                "minimum_directly_metered_fraction": min(row["directly_metered_fraction"] for row in group),
                "maximum_directly_metered_fraction": max(row["directly_metered_fraction"] for row in group),
                "median_controller_process_envelope_residual_ns": statistics.median(
                    row["phases_ns"]["controller_process_envelope_residual_ns"] for row in group
                ),
            }
        )
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.v11_cold_phase_ledger.v1",
        "date": "2026-08-24",
        "status": "PASS__144_EXISTING_COLD_RECEIPTS_RECOUNTED__NO_NEW_TIMING",
        "source": identity(V11_EVIDENCE),
        "scope": {
            "operation": "UNREGISTERED_DIAGNOSTIC_RECOUNT_OF_IMMUTABLE_GOAL5798_V11_RECEIPTS",
            "new_application_execution_count": 0,
            "new_registered_timing_count": 0,
            "formal_performance_claim_added": False,
        },
        "phase_definition": {
            "top_level_phases_are_mutually_exclusive": True,
            "input_materialization_ns": "direct worker timer",
            "common_preparation_total_ns": "direct worker timer; subphase timers are nested and are not added again",
            "complete_execute_ns": "sum of direct worker execute timers",
            "close_ns": "direct worker timer where emitted; explicit zero where the arm emitted null",
            "controller_process_envelope_residual_ns": "controller wall minus the four directly metered top-level phases; named subtraction only, with no causal attribution",
        },
        "counts": {
            "cold_receipts": len(rows),
            "tasks": len({row["task"] for row in rows}),
            "arms": len({row["arm"] for row in rows}),
            "cells": len(counts),
            "samples_per_cell": sorted(set(counts.values())),
            "negative_residual_rows": sum(
                row["phases_ns"]["controller_process_envelope_residual_ns"] < 0 for row in rows
            ),
            "named_accounting_fraction_below_one_rows": sum(row["named_accounting_fraction"] != 1.0 for row in rows),
            "directly_metered_fraction_below_0_95_rows": sum(row["directly_metered_fraction"] < 0.95 for row in rows),
        },
        "summaries": summaries,
        "rows": rows,
        "claim_boundary": {
            "all_wall_time_named": True,
            "all_wall_time_directly_metered": False,
            "envelope_residual_is_safety_or_checker_tax": False,
            "goal5802_must_directly_meter_at_least_95_percent_or_report_failure": True,
            "these_diagnostic_numbers_may_replace_goal5798_registered_results": False,
        },
        "rows_sha256": sha(canonical_json_bytes(rows)),
        "phase_ledger_sha256": "",
    }
    return _sealed(document, "phase_ledger")


def build_contract() -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.performance_and_evidence_contract.v1",
        "date": "2026-08-24",
        "status": "FROZEN__DESIGN_ONLY__NO_FORMAL_EXECUTION_AUTHORIZED",
        "scientific_question": "What additional cost does RTDL's whole-protocol checking add beyond an idiomatic hosted OptiX binding, while preserving exact functional work?",
        "claim_ceiling": {
            "primary": "NONINFERIORITY_TO_IDIOMATIC_PYOPTIX_AT_MATCHED_HOST_LANGUAGE_SCOPE",
            "rtdl_speedup_over_same_backend": "PRESUMPTIVE_INSTRUMENT_DEFECT__INVESTIGATE_BEFORE_ANY_CLAIM",
            "direct_cuda_optix_gap": "HOST_LANGUAGE_AND_STACK_CONTEXT__NOT_ATTRIBUTABLE_TO_RTDL_CHECKER_WITHOUT_CAUSAL_EVIDENCE",
            "owl_performance": "NO_CLAIM_UNLESS_AN_EXACT_MATCHED_EXECUTABLE_ARM_IS_MEASURED",
        },
        "comparative_gates": {
            "STEADY_E2E": {
                "enabled": True,
                "metric": "RTDL/PYOPTIX",
                "decision": "95_PERCENT_CI_UPPER_BOUND_LE_1.05",
            },
            "PREPARE": {
                "enabled": True,
                "metric": "RTDL/PYOPTIX",
                "decision": "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
            },
            "DEPLOYMENT_COLD": {
                "enabled": True,
                "metric": "RTDL/PYOPTIX",
                "decision": "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
            },
            "BUILD_COLD": {
                "enabled": False,
                "publication": "ABSOLUTE_TIME_PLUS_AMORTIZATION_POINT_ONLY",
            },
            "ON_BYPASS": {
                "enabled": False,
                "publication": "STRUCTURAL_IDENTITY_AND_FALSIFIABLE_CACHE_HIT_NEGATIVE_ASSERTIONS_ONLY",
            },
            "GPU_KERNEL": {
                "enabled": False,
                "publication": "SANITY_IDENTITY_ONLY__NO_COMPARATIVE_PERFORMANCE_GATE",
            },
        },
        "structural_cache_hit_assertions": {
            "exact_ptx_identity": True,
            "exact_program_group_pipeline_sbt_launch_parameter_identity": True,
            "same_launch_and_synchronization_counts": True,
            "same_exact_output_and_oracle": True,
            "cache_hit_imports_numba": False,
            "cache_hit_invokes_nvrtc": False,
            "cache_hit_invokes_rtdl_compiler_or_codegen": False,
            "observation_method": "fresh-process import interception plus NVRTC/compiler call interception; any hit fails the assertion",
        },
        "baselines": {
            "DIRECT_CUDA_OPTIX": {
                "role": "expert native context row; never silently omitted",
                "first_class_publication_row": True,
            },
            "PYOPTIX": {
                "role": "primary hosted-language performance baseline",
                "repository_commit": "3144f224c0fd18733925faf3d8fb82c7376b8dcf",
                "repository_tree": "0bf0ec24efb4a43f129aee25dd265aa8149374e3",
                "idiomatic_requirements": [
                    "public API except a separately disclosed absence in upstream capability",
                    "bulk ndarray/list conversion outside timed region where conversion is not user-visible output work",
                    "no per-element Python loop in a timed path when a standard bulk operation exists",
                    "no debug, receipt serialization, forensic hashing, or oracle construction in timed region",
                    "same functional output, status obligations, launches, synchronizations, and oracle boundary as RTDL",
                    "exact timed source embedded in the Goal5802 sole CFR",
                ],
            },
            "OWL": {
                "role": "executable residual-responsibility arm; full timing optional",
                "repository_commit": "df7390b16bce5244b7352ca6d3e320f838297072",
                "repository_tree": "c31d2c7510050fc3d57a4c4e0a4d4d84bc7b03ff",
                "minimum_residual_mechanisms_required": 3,
                "mechanisms_total": 5,
            },
        },
        "symmetry": {
            "same_timer_boundaries": True,
            "same_data_and_exact_oracle": True,
            "same_launch_and_sync_semantics": True,
            "same_output_materialization_semantics": True,
            "forbid_per_arm_postresult_optimization": True,
            "arm_engineering_ledger_fields": [
                "arm",
                "engineer_or_agent",
                "start_utc",
                "stop_utc",
                "active_minutes",
                "files_changed",
                "purpose",
                "result_seen_before_change",
            ],
            "mandatory_preworker_external_question": "Would a competent PyOptiX/OWL developer write and time each arm this way?",
            "mandatory_preworker_acceptable_answer": "YES_WITH_ZERO_P0_OR_P1",
        },
        "phase_attribution": {
            "minimum_directly_metered_wall_fraction": 0.95,
            "mutually_exclusive_phases_required": True,
            "unaccounted_time_must_be_named_not_dropped": True,
            "subtraction_residual_is_not_causal_attribution": True,
            "required_named_phases": [
                "input materialization",
                "protocol validation and code generation",
                "device compilation",
                "GAS/static preparation",
                "module/program/pipeline/SBT preparation",
                "complete execute including required output materialization",
                "close",
                "controller/process envelope",
            ],
        },
        "amortization": {
            "publish_direct_over_pyoptix_ratio": True,
            "publish_build_cold_absolute_times": True,
            "equation": "B_RTDL + D_RTDL + N*S_RTDL <= D_PYOPTIX + N*S_PYOPTIX",
            "break_even_if_s_pyoptix_gt_s_rtdl": "ceil(max(0, B_RTDL + D_RTDL - D_PYOPTIX) / (S_PYOPTIX - S_RTDL))",
            "if_no_finite_break_even": "publish NEVER",
            "scenario_assumptions_required": True,
        },
        "mandatory_rtdlexe_attacks": [
            "schema_version_downgrade_or_rollback",
            "partial_chain_or_missing_nested_authority",
            "confused_deputy_cross_task_or_cross_device_family",
            "cache_poisoning_with_rehash_and_reseal",
            "cache_hit_attempting_compiler_numba_or_nvrtc_execution",
        ],
        "publication": {
            "direct_pyoptix_rtdl_three_rows_every_regime": True,
            "every_diagnostic_number_prefixed_UNREGISTERED_DIAGNOSTIC": True,
            "v11_withdrawal_sentence": "The initially favorable prepared comparison was withdrawn after review found avoidable per-element Python work in the PyOptiX arm; the correction removes an RTDL-favorable measurement bias.",
            "prominent_limits": {
                "new_app_generalization_exams": 0,
                "third_party_usability_studies": 0,
                "functionally_matched_cuda_optix_productivity_baselines": 0,
            },
        },
        "goal5803_descope": {
            "decision_cutoff": "2026-08-27T23:59:59-04:00",
            "required_before_any_entry": [
                "external acceptance of exact 200-work exposure registry",
                "frozen disjoint task identity resolved by registry lookup",
                "separate owner authority",
            ],
            "default_after_cutoff": "PAPER_PLANNED_WITH_ZERO_EXTERNAL_EVIDENCE",
            "participant_study": "POST_SUBMISSION_FOLLOWUP",
        },
        "anonymity": {
            "artifact_evidence_gate": "separate exact scan of archives, paths, manifests, usernames, hosts, commit metadata, acknowledgments, and embedded history",
            "manuscript_gate": "separate CGO review-anonymous scan of prose, metadata, PDFs, supplemental files, and repository links",
            "one_gate_may_substitute_for_the_other": False,
        },
        "authorization": {
            "goal5800_local_untimed": True,
            "goal5801_local_untimed": True,
            "goal5802_design_and_exact_cfr": True,
            "goal5802_formal_worker_zero": False,
            "goal5802_pod_gpu_timing": False,
            "goal5803": False,
            "submission_or_public_claim": False,
        },
        "contract_sha256": "",
    }
    validate_contract(document)
    return _sealed(document, "contract")


def validate_contract(document: Mapping[str, Any]) -> None:
    gates = document.get("comparative_gates")
    if not isinstance(gates, Mapping):
        raise Goal5799Error("CONTRACT_GATES_MISSING")
    for name in ("STEADY_E2E", "PREPARE", "DEPLOYMENT_COLD"):
        if not isinstance(gates.get(name), Mapping) or gates[name].get("enabled") is not True:
            raise Goal5799Error(f"REQUIRED_GATE_DISABLED:{name}")
    for name in ("BUILD_COLD", "ON_BYPASS", "GPU_KERNEL"):
        if not isinstance(gates.get(name), Mapping) or gates[name].get("enabled") is not False:
            raise Goal5799Error(f"FORBIDDEN_OR_TAUTOLOGICAL_GATE_ENABLED:{name}")
    baselines = document.get("baselines")
    if not isinstance(baselines, Mapping):
        raise Goal5799Error("BASELINES_MISSING")
    direct = baselines.get("DIRECT_CUDA_OPTIX")
    pyoptix = baselines.get("PYOPTIX")
    owl = baselines.get("OWL")
    if not isinstance(direct, Mapping) or direct.get("first_class_publication_row") is not True:
        raise Goal5799Error("DIRECT_BASELINE_NOT_FIRST_CLASS")
    if not isinstance(pyoptix, Mapping):
        raise Goal5799Error("PYOPTIX_BASELINE_MISSING")
    requirements = pyoptix.get("idiomatic_requirements")
    if not isinstance(requirements, list) or not any("no per-element Python loop" in item for item in requirements):
        raise Goal5799Error("PYOPTIX_PER_ELEMENT_TIMING_BAN_MISSING")
    if not isinstance(owl, Mapping) or owl.get("minimum_residual_mechanisms_required") != 3:
        raise Goal5799Error("OWL_EXECUTABLE_RESIDUAL_REQUIREMENT_MISSING")
    ceiling = document.get("claim_ceiling")
    if not isinstance(ceiling, Mapping) or "INSTRUMENT_DEFECT" not in str(ceiling.get("rtdl_speedup_over_same_backend")):
        raise Goal5799Error("BACKEND_SPEEDUP_INSTRUMENT_GUARD_MISSING")
    structural = document.get("structural_cache_hit_assertions")
    if not isinstance(structural, Mapping):
        raise Goal5799Error("CACHE_HIT_ASSERTIONS_MISSING")
    for key in ("cache_hit_imports_numba", "cache_hit_invokes_nvrtc", "cache_hit_invokes_rtdl_compiler_or_codegen"):
        if structural.get(key) is not False:
            raise Goal5799Error(f"CACHE_HIT_NEGATIVE_ASSERTION_MISSING:{key}")
    symmetry = document.get("symmetry")
    if not isinstance(symmetry, Mapping) or symmetry.get("mandatory_preworker_acceptable_answer") != "YES_WITH_ZERO_P0_OR_P1":
        raise Goal5799Error("PREWORKER_COMPETENCE_REVIEW_MISSING")
    if len(symmetry.get("arm_engineering_ledger_fields", [])) < 8:
        raise Goal5799Error("ENGINEERING_EFFORT_LEDGER_INCOMPLETE")
    phase = document.get("phase_attribution")
    if not isinstance(phase, Mapping) or phase.get("minimum_directly_metered_wall_fraction") != 0.95:
        raise Goal5799Error("PHASE_COVERAGE_GATE_MISSING")
    attacks = document.get("mandatory_rtdlexe_attacks")
    if not isinstance(attacks, list) or len(attacks) != 5:
        raise Goal5799Error("RTDLEXE_ATTACK_SET_INCOMPLETE")
    publication = document.get("publication")
    if not isinstance(publication, Mapping) or publication.get("direct_pyoptix_rtdl_three_rows_every_regime") is not True:
        raise Goal5799Error("THREE_ROW_PUBLICATION_RULE_MISSING")
    authorization = document.get("authorization")
    if not isinstance(authorization, Mapping):
        raise Goal5799Error("AUTHORIZATION_MISSING")
    for key in ("goal5802_formal_worker_zero", "goal5802_pod_gpu_timing", "goal5803", "submission_or_public_claim"):
        if authorization.get(key) is not False:
            raise Goal5799Error(f"LOCKED_ACTION_AUTHORIZED:{key}")


def build_result(absorption: Mapping[str, Any], ledger: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.local_completion_result.v1",
        "date": "2026-08-24",
        "status": "PASS__GOAL5799_LOCAL_SCOPE_COMPLETE__EXTERNAL_REVIEW_REQUESTED",
        "inputs": [identity(path) for path in PINNED_INPUTS],
        "outputs": [identity(path) for path in (ABSORPTION, PHASE_LEDGER, CONTRACT)],
        "completed": {
            "returned_review_absorbed": True,
            "performance_contract_made_executable": True,
            "tautological_timing_gates_removed": True,
            "baseline_symmetry_operationalized": True,
            "direct_pyoptix_publication_row_required": True,
            "build_cold_amortization_required": True,
            "five_rtdlexe_attacks_frozen": True,
            "two_anonymity_gates_frozen": True,
            "goal5803_dated_descope_frozen": True,
            "observed_200_work_registry_built_and_independently_verified": True,
            "goal5797_populated_leaf_local_evidence": "19_OF_19_DECISION_BEARING__EXTERNAL_REVIEW_PENDING",
            "existing_v11_cold_receipts_recounted": 144,
            "new_timing_samples": 0,
        },
        "scientific_state": {
            "new_app_generalization_exam_count": 0,
            "third_party_usability_study_count": 0,
            "executable_owl_residual_mechanisms_demonstrated": 0,
            "goal5797_mechanisms_with_single_leaf_accept_to_reject_witness": 5,
            "goal5797_populated_contract_leaves_with_accept_to_reject_witness": 19,
            "goal5798_v11_prepared_win_claim_active": False,
            "performance_noninferiority_to_idiomatic_pyoptix_established": False,
        },
        "remaining_minimum_cgo_work": [
            "Goal5800 executable OWL residual arm demonstrating at least 3 of 5 mechanisms",
            "Goal5801 public lifecycle plus sealed .rtdlexe artifact and five mandatory hostile attacks",
            "Goal5802 externally reviewed symmetric measurement design and only then formal execution",
            "manuscript and artifact anonymity gates plus prominent capability limits",
        ],
        "locks": {
            "goal5802_formal_measurement": True,
            "goal5803_external_evidence": True,
            "provider_network": True,
            "pod_gpu_timing": True,
            "submission_claim": True,
        },
        "bound_seals": {
            "absorption_sha256": absorption.get("absorption_sha256"),
            "phase_ledger_sha256": ledger.get("phase_ledger_sha256"),
            "contract_sha256": contract.get("contract_sha256"),
        },
        "result_sha256": "",
    }
    return _sealed(document, "result")


def _markdown_identity(path: Path) -> str:
    item = identity(path)
    return f"`{item['path']}` — {item['bytes']:,} bytes — SHA-256 `{item['sha256']}`"


def build_self_review(result: Mapping[str, Any], ledger: Mapping[str, Any]) -> bytes:
    below = ledger["counts"]["directly_metered_fraction_below_0_95_rows"]
    text = f"""# Strict self-review — Goal5799 local completion (2026-08-24)

## Verdict

**PASS at bounded local Goal5799 scope; external acceptance remains pending.** This work absorbs the returned review, freezes an executable successor contract, registers the exact 200 observed X3 works as permanently ineligible, and packages the pending Goal5797-A1 evidence. It does not create generalization evidence, usability evidence, OWL evidence, or a performance result.

## Anti-stupidity three questions applied

1. Could history answer what Goal5799 meant? Yes: the exact reviewed CFR and returned review were pinned and used; no new meaning was requested from the owner.
2. Could local machine inspection answer the evidence questions? Yes: the sealed journal, A1 result, v11 archive, candidate worker sources, and registry were reconstructed locally and offline.
3. Could conservative assumptions avoid authority expansion? Yes: every ambiguous permission was held false. Goal5802 formal execution, Goal5803, network, POD timing, participants, and submission remain locked.

## Hard self-findings

1. **The old v11 phase data do not satisfy the future 95% direct-metering requirement.** All 144 cold walls are named exactly only because `controller_process_envelope_residual` is computed by subtraction; {below}/144 rows have directly metered coverage below 95%. The ledger makes the missing envelope visible but does not explain it and does not call it checker or safety cost. Goal5802 must instrument it or report failure.
2. **Goal5797-A1 is locally strong but not externally accepted.** Nineteen of nineteen populated leaves are decision-bearing in two frozen contracts, including `require_status_ok`; this is not yet a universal language theorem and it remains a requested ruling in the sole CFR.
3. **The 200-work registry repairs contamination bookkeeping, not generalization.** It adds zero exams and zero candidates. The Goal5793 branch remains terminal-negative.
4. **OWL evidence is still zero.** The contract demands an executable residual arm with at least 3/5 mechanisms; prose comparison cannot close Goal5800.
5. **Performance is still unresolved.** The favorable v11 prepared claim remains withdrawn. The new contract prevents a repeat of asymmetric Python work but supplies no new measurement.

## What the contract now rejects

- Reintroducing ON/bypass or GPU-kernel comparative gates.
- Omitting Direct/PyOptiX as a first-class contextual row.
- Timing avoidable per-element Python work in one arm.
- Treating an RTDL speedup over the same hosted backend as a scientific win before instrument audit.
- Starting formal Goal5802 workers without exact pre-worker review.
- Entering Goal5803 before external acceptance of the exact 200-work registry and a separate owner authority.

## Claim ceiling

Goal5799 supports only this process claim: the next two local implementation goals now have a review-derived, fail-closed target. It does not support “easy,” “general,” “faster,” “no overhead,” “OWL cannot,” or submission-ready claims.

Exact local result seal: `{result['result_sha256']}`.
"""
    return text.encode("utf-8")


def _tar_member(path: Path, member_name: str) -> bytes:
    with tarfile.open(path, "r:gz") as archive:
        member = archive.extractfile(member_name)
        if member is None:
            raise Goal5799Error(f"CANDIDATE_MEMBER_MISSING:{member_name}")
        return member.read()


def _embed(title: str, path: Path, language: str = "text") -> str:
    payload = path.read_bytes()
    try:
        body = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise Goal5799Error(f"EMBED_NON_UTF8:{path.name}") from exc
    fence = "````````"
    return (
        f"\n## Embedded: {title}\n\n"
        f"Identity: {_markdown_identity(path)}\n\n"
        f"{fence}{language}\n{body}"
        + ("\n" if not body.endswith("\n") else "")
        + f"{fence}\n"
    )


def build_cfr(result: Mapping[str, Any]) -> bytes:
    worker_members = [
        "source/experiments/goal5798_premeasurement/worker_common.py",
        "source/experiments/goal5798_premeasurement/rtdl_worker.py",
        "source/experiments/goal5798_premeasurement/pyoptix_worker.py",
    ]
    worker_sections = []
    for member_name in worker_members:
        payload = _tar_member(V11_CANDIDATE, member_name)
        worker_sections.append(
            "\n## Embedded candidate member: "
            + member_name
            + f"\n\nBytes `{len(payload)}`; SHA-256 `{sha(payload)}`; parent archive `{identity(V11_CANDIDATE)['sha256']}`.\n\n"
            + "````````python\n"
            + payload.decode("utf-8", errors="strict")
            + ("\n" if not payload.endswith(b"\n") else "")
            + "````````\n"
        )
    header = f"""# SEND ONLY THIS FILE — Call for review: Goal5799 local completion and Goal5800/5801 entry

**This Markdown file is the sole external-review delivery. Do not send a packet, archive, or second CFR.** It embeds the review, exact terminal journal, registry implementation/results, pending Goal5797-A1 single-file CFR, Goal5799 contract/result/self-review, and the v11 worker sources needed to inspect phase boundaries. Large immutable v11 archives remain named by local path and digest; they are not additional delivery files.

## Requested verdict

Return `P0 / P1 / P2 / P3` and answer every question:

1. Does the exact 200-row registry close the Goal5793-X3 exposure-bookkeeping P1 while keeping Goal5793 terminal, every observed row ineligible, and generalization exams at zero?
2. Does the embedded Goal5797-A1 evidence establish that all 19 populated leaves in the two frozen contracts are decision-bearing, including `role_effects.finalize -> require_status_ok`, at exactly that scope?
3. Does the Goal5799 contract correctly remove tautological ON/bypass and GPU-kernel comparative gates and retain only falsifiable STEADY_E2E, PREPARE, and DEPLOYMENT_COLD gates?
4. Are idiomatic PyOptiX/OWL, equal timer boundaries, per-arm engineering effort, the pre-worker competence question, Direct/PyOptiX publication, and backend noninferiority ceiling frozen strongly enough to prevent v11's asymmetric-instrument recurrence?
5. Is the phase ledger honest: 144 old cold receipts, zero new timings, 100% named wall only by explicit subtraction residual, no causal attribution, and a future >=95% directly-metered requirement?
6. Does the 2026-08-27 cutoff/descope close the schedule P1 without fabricating external evidence?
7. May Goal5800 and Goal5801 proceed locally and untimed after owner absorption, while Goal5802 formal workers, Goal5803, provider network, POD timing, participants, submission, and public claims remain locked?
8. Are there any missing exact-byte attacks or anonymity conditions that would make the proposed Goal5802 evidence unsafe?

## Current result, without sales language

- Goal5797 local leaf sweep: **19/19 decision-bearing**, external ruling pending.
- Goal5793 observed works: **200/200 registered, 0 eligible**; this adds **0 generalization exams**.
- Goal5798 v11 favorable prepared claim: **withdrawn**; no successor measurement has run.
- Goal5799: returned review absorbed; executable future contract frozen; **0 new application runs, 0 new timings, 0 OWL residual demonstrations, 0 usability studies**.
- Minimum CGO-critical next work remains executable OWL residual evidence, public `.rtdlexe` lifecycle/attacks, and symmetric performance measurement after exact pre-worker review.

Local result seal: `{result['result_sha256']}`.

## External dependencies named but not sent

- {_markdown_identity(V11_EVIDENCE)}
- {_markdown_identity(V11_CANDIDATE)}

The phase ledger derives only from the first archive. The exact worker source members below derive from the second archive. Neither archive is authorization to rerun.
"""
    sections = [header]
    sections.append(_embed("returned Goal5799 review", RETURNED_REVIEW, "markdown"))
    sections.append(_embed("Goal5799 reviewed plan CFR", PLAN_CFR, "markdown"))
    sections.append(_embed("Goal5799 review absorption", ABSORPTION, "json"))
    sections.append(_embed("Goal5799 performance/evidence contract", CONTRACT, "json"))
    sections.append(_embed("Goal5799 v11 cold phase ledger", PHASE_LEDGER, "json"))
    sections.append(_embed("Goal5799 local completion result", RESULT, "json"))
    sections.append(_embed("Goal5799 strict self-review", SELF_REVIEW, "markdown"))
    sections.append(_embed("Goal5797-A1 sole CFR pending review", A1_CFR, "markdown"))
    sections.append(_embed("Goal5793-X3 terminal owner closure/A1 entry", X3_CLOSURE, "json"))
    sections.append(_embed("Goal5793-X3 exact terminal journal", X3_JOURNAL, "jsonl"))
    sections.append(_embed("Goal5793-X3-A1 exposure registry", X3_REGISTRY, "json"))
    sections.append(_embed("Goal5793-X3-A1 independent verification", X3_REGISTRY_VERIFICATION, "json"))
    sections.append(_embed("Goal5793-X3-A1 registry builder", ROOT / "scripts/goal5793_x3_a1_build_observed_exposure_registry.py", "python"))
    sections.append(_embed("Goal5793-X3-A1 independent verifier", ROOT / "scripts/goal5793_x3_a1_independent_verify_observed_exposure_registry.py", "python"))
    sections.append(_embed("Goal5793-X3-A1 hostile tests", ROOT / "tests/goal5793_x3_a1_observed_exposure_registry_test.py", "python"))
    sections.append(_embed("Goal5799 builder", Path(__file__).resolve(), "python"))
    sections.append(_embed("Goal5799 hostile tests", ROOT / "tests/goal5799_local_completion_test.py", "python"))
    sections.extend(worker_sections)
    sections.append(
        "\n## Required return format\n\n"
        "Commit one review Markdown file naming this CFR SHA-256, verdict, every requested answer, exact counterexamples for every P0/P1, and an explicit statement that no formal Goal5802 execution or Goal5803 entry is authorized unless separately granted.\n"
    )
    return "".join(sections).encode("utf-8")


def _payload(document: Mapping[str, Any]) -> bytes:
    return canonical_json_bytes(document) + b"\n"


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise Goal5799Error(f"CREATE_ONLY_OUTPUT_EXISTS:{path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def construct_payloads() -> dict[Path, bytes]:
    verify_pinned_inputs()
    absorption = build_absorption()
    ledger = build_phase_ledger()
    contract = build_contract()
    # Identity-bearing result is constructed after the first three artifacts
    # exist.  Dry-run callers receive deterministic placeholder identities.
    return {
        ABSORPTION: _payload(absorption),
        PHASE_LEDGER: _payload(ledger),
        CONTRACT: _payload(contract),
    }


def write_all_create_only() -> dict[str, Any]:
    for path in OUTPUTS:
        if path.exists() or path.is_symlink():
            raise Goal5799Error(f"CREATE_ONLY_OUTPUT_EXISTS:{path.name}")
    first = construct_payloads()
    for path, payload in first.items():
        _write_create_only(path, payload)
    absorption = json.loads(ABSORPTION.read_text(encoding="utf-8"))
    ledger = json.loads(PHASE_LEDGER.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    result = build_result(absorption, ledger, contract)
    _write_create_only(RESULT, _payload(result))
    self_review = build_self_review(result, ledger)
    _write_create_only(SELF_REVIEW, self_review)
    cfr = build_cfr(result)
    _write_create_only(CFR, cfr)
    return {"status": "CREATE_ONLY_WRITE_PASS", "outputs": [identity(path) for path in OUTPUTS]}


def verify_stored() -> dict[str, Any]:
    verify_pinned_inputs()
    absorption = build_absorption()
    ledger = build_phase_ledger()
    contract = build_contract()
    expected_first = {
        ABSORPTION: _payload(absorption),
        PHASE_LEDGER: _payload(ledger),
        CONTRACT: _payload(contract),
    }
    for path, payload in expected_first.items():
        if path.read_bytes() != payload:
            raise Goal5799Error(f"STORED_OUTPUT_MISMATCH:{path.name}")
    result = build_result(absorption, ledger, contract)
    if RESULT.read_bytes() != _payload(result):
        raise Goal5799Error("STORED_OUTPUT_MISMATCH:result")
    ledger_stored = json.loads(PHASE_LEDGER.read_text(encoding="utf-8"))
    if SELF_REVIEW.read_bytes() != build_self_review(result, ledger_stored):
        raise Goal5799Error("STORED_OUTPUT_MISMATCH:self_review")
    if CFR.read_bytes() != build_cfr(result):
        raise Goal5799Error("STORED_OUTPUT_MISMATCH:cfr")
    return {"status": "POSTWRITE_VERIFY_PASS", "outputs": [identity(path) for path in OUTPUTS]}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-create-only", action="store_true")
    mode.add_argument("--verify-stored", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.write_create_only:
        result = write_all_create_only()
    elif args.verify_stored:
        result = verify_stored()
    else:
        first = construct_payloads()
        result = {
            "status": "DRY_RUN_PASS",
            "outputs": [
                {"path": path.relative_to(ROOT).as_posix(), "bytes": len(payload), "sha256": sha(payload)}
                for path, payload in first.items()
            ],
        }
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
