#!/usr/bin/env python3
"""Rebuild the internal hostile self-audit of Goals5835 and 5836.

The historical Goal5835/5836 authorities remain immutable.  This audit checks
their exact bytes, independently reruns the portable part of the Goal5835
receipt, and records counterexamples that bound what the result can mean.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from case_studies.sui_derived_edge_crossing_core import (  # noqa: E402
    ObstacleTriangle,
    SweptSphereSegment,
    deduplicate_triangle_edges,
    execute_registered_problem,
)
from case_studies.sui_derived_edge_crossing_core.fixtures import (  # noqa: E402
    load_registered_cases,
)
from case_studies.sui_derived_edge_crossing_core import (  # noqa: E402
    run_functional_receipt as goal5835_receipt,
)
from scripts import goal5836_a0_build_source_acquisition as a0  # noqa: E402
from scripts import goal5836_a1_build_source_fidelity as a1  # noqa: E402
from scripts import goal5836_build_sui_same_input_preaction as preaction  # noqa: E402


OUTPUT_RELATIVE = (
    "history/internal_docs/goal5835_goal5836_strict_audit_20260901"
)
DEFAULT_OUTPUT = ROOT / OUTPUT_RELATIVE
AUTHORITY_FILENAME = "STRICT_AUDIT_AUTHORITY.json"
DOMAIN = b"rtdl.goal5835_goal5836.strict_audit.v1\0"

PATHS = {
    "fixture_authority": (
        "history/internal_docs/goal5834_b1_fixture_preaction_20260830/"
        "FIXTURE_AUTHORITY.json"
    ),
    "worker_inputs": (
        "history/internal_docs/goal5834_b1_fixture_preaction_20260830/"
        "WORKER_INPUTS.json"
    ),
    "b3_raw": (
        "history/internal_docs/goal5834_b3_home_result_20260830/"
        "RAW_GPU_RECEIPT_B3.json"
    ),
    "b3_evaluation": (
        "history/internal_docs/goal5834_b3_home_result_20260830/"
        "INDEPENDENT_EVALUATION_B3.json"
    ),
    "goal5835_result": (
        "history/internal_docs/"
        "goal5835_sui_derived_edge_crossing_mapping_result_20260830.json"
    ),
    "goal5835_recount": (
        "history/internal_docs/"
        "goal5835_sui_derived_edge_crossing_mapping_recount_20260830.json"
    ),
    "goal5835_receipt_source": (
        "case_studies/sui_derived_edge_crossing_core/"
        "run_functional_receipt.py"
    ),
    "goal5835_core_source": (
        "case_studies/sui_derived_edge_crossing_core/"
        "bounded_piecewise_linear_core.py"
    ),
    "goal5835_fixture_source": (
        "case_studies/sui_derived_edge_crossing_core/fixtures.py"
    ),
    "goal5835_readme": (
        "case_studies/sui_derived_edge_crossing_core/README.md"
    ),
    "goal5836_a1_authority": (
        "history/internal_docs/goal5836_a1_source_fidelity_20260901/"
        "SOURCE_FIDELITY_AUTHORITY.json"
    ),
    "paper_main": "paper/cgo2027/main.tex",
}

EXPECTED_SHA256 = {
    "fixture_authority": (
        "0f13ab8a7408c253114c56a51645c015d0e5e36ca96a4290c9dd1a2ba700adad"
    ),
    "worker_inputs": (
        "55eeff377c93c32fed8cc326ad975cb9d2437df85812e30b9d916b3e7cc581a4"
    ),
    "b3_raw": (
        "b50043e81713aacf6a70986a6e334789cbfeef17342ae97a8ae401ab1507f513"
    ),
    "b3_evaluation": (
        "786ebd4970dadf842c57aa6c08539694d0cdbe8a6b2f6672932029b5f19be02a"
    ),
    "goal5835_result": (
        "ae370da1ca5ac96562d0956438e7c6c8eee39fddf2d9894953db8e956c47ccff"
    ),
    "goal5835_recount": (
        "ae370da1ca5ac96562d0956438e7c6c8eee39fddf2d9894953db8e956c47ccff"
    ),
    "goal5835_receipt_source": (
        "ceb038092790f6a54ae84f455021769f00f42a618da8e84c7192b404a778717c"
    ),
    "goal5835_core_source": (
        "65e61185117a9cb052a1b4a6c29cc83346f9405911231784b7f2cd8b5eb0952f"
    ),
    "goal5835_fixture_source": (
        "a204010d9bd2794da6fb1972f895232e4e51f0549bf82028e3891871de471bc5"
    ),
    "goal5835_readme": (
        "b8ff0817518785635d005665601b7590664e01a1854a860d39ea604e290abdbd"
    ),
    "goal5836_a1_authority": (
        "f05b026c2e96506466a400de71ee8ab6893f8deecb547447f29b8af567842c5f"
    ),
}

EXPECTED_FINDINGS = {
    "P1-G5835-CLAIM-SCOPE",
    "P2-G5835-NO-POSITIVE-MESH",
    "P2-G5835-SYNTHETIC-SPHERE-IDENTITY",
    "P2-G5835-OUTPUT-FAIL-CLOSED",
    "P2-G5835-DUPLICATE-TRIANGLE-DIRECTION",
    "P2-G5835-PATH-DEPENDENT-RECEIPT",
    "P3-G5835-PERMISSIVE-ID-TYPES",
    "P2-G5836-HUMAN-SEMANTIC-STEP",
}


class StrictAuditError(RuntimeError):
    """Raised when the strict audit cannot reproduce its frozen facts."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _pretty(value: Any) -> bytes:
    return json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii") + b"\n"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _identity(label: str) -> dict[str, Any]:
    relative = PATHS[label]
    data = (ROOT / relative).read_bytes()
    return {
        "path": relative,
        "bytes": len(data),
        "sha256": _sha256(data),
    }


def _load_json(relative: str) -> Any:
    return json.loads(
        (ROOT / relative).read_text(encoding="ascii", errors="strict"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {value}")
        ),
    )


def _without_source_paths(document: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(document)
    for row in value["application_sources"]:
        row.pop("path", None)
    return value


def _direct_call_names(source: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return names


def _receipt_args() -> SimpleNamespace:
    return SimpleNamespace(
        fixture_authority=ROOT / PATHS["fixture_authority"],
        worker_inputs=ROOT / PATHS["worker_inputs"],
        raw_receipt=ROOT / PATHS["b3_raw"],
        b3_evaluation=ROOT / PATHS["b3_evaluation"],
    )


def _duplicate_triangle_direction_probe() -> dict[str, Any]:
    first = ObstacleTriangle(
        "dup", ("a", "b", "c"),
        ((0, 0, 0), (1, 0, 0), (0, 1, 0)),
    )
    second = ObstacleTriangle(
        "dup", ("b", "a", "d"),
        ((1, 0, 0), (0, 0, 0), (1, 1, 0)),
    )
    forward = deduplicate_triangle_edges((first, second))
    reverse = deduplicate_triangle_edges((second, first))
    forward_shared = next(row for row in forward if row.edge_id == "a--b")
    reverse_shared = next(row for row in reverse if row.edge_id == "a--b")
    return {
        "duplicate_triangle_ids_rejected": False,
        "input_order_invariant": forward == reverse,
        "forward_shared_direction": [
            list(forward_shared.start), list(forward_shared.end),
        ],
        "reverse_shared_direction": [
            list(reverse_shared.start), list(reverse_shared.end),
        ],
    }


def _malformed_output_probe(problem: Any) -> dict[str, Any]:
    generic = SimpleNamespace(
        per_query_hit=(1,),
        any_hit=0,
        output_sha256="a" * 64,
        physical_receipt={},
        traversal_receipt={},
    )

    class Prepared:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def execute(self, _batch):
            return generic

    materialized = SimpleNamespace(prepare=lambda _static: Prepared())
    result = execute_registered_problem(materialized, problem)
    return {
        "malformed_output_rejected": False,
        "edge_count": len(result.edge_ids),
        "bit_count": len(result.per_edge_hit),
        "reported_collision": result.collision,
        "computed_or": int(any(result.per_edge_hit)),
    }


def _seal(document: dict[str, Any]) -> str:
    payload = dict(document)
    payload["strict_audit_authority_sha256"] = ""
    return _sha256(DOMAIN + _canonical(payload))


def build_authority() -> dict[str, Any]:
    identities = {label: _identity(label) for label in EXPECTED_SHA256}
    for label, expected in EXPECTED_SHA256.items():
        if identities[label]["sha256"] != expected:
            raise StrictAuditError(f"HISTORICAL_IDENTITY_DRIFT:{label}")

    if (ROOT / PATHS["goal5835_result"]).read_bytes() != (
            ROOT / PATHS["goal5835_recount"]).read_bytes():
        raise StrictAuditError("GOAL5835_RESULT_RECOUNT_DIFFER")

    preaction_authority = preaction.verify_stored()
    a0_authority = a0.verify_stored()
    a1_authority = a1.verify_stored()
    historical_result = _load_json(PATHS["goal5835_result"])
    regenerated = goal5835_receipt.build_receipt(_receipt_args())
    semantic_regeneration_equal = (
        _without_source_paths(historical_result)
        == _without_source_paths(regenerated)
    )
    if not semantic_regeneration_equal:
        raise StrictAuditError("GOAL5835_SEMANTIC_REGENERATION_DIFFER")

    cases = load_registered_cases(
        ROOT / PATHS["fixture_authority"],
        ROOT / PATHS["worker_inputs"],
    )
    piecewise = next(
        row for row in cases if row.execution_id == "piecewise_linear_or"
    )
    complete_mesh_positive_rows = [
        row["execution_id"]
        for row in historical_result["rows"]
        if row["collision"] == 1
        and row["identity_projection"]["query_to_edge"]
        and all(
            query["source_triangle_ids"]
            for query in row["identity_projection"]["query_to_edge"]
        )
    ]
    complete_mesh_rows = [
        row["execution_id"]
        for row in historical_result["rows"]
        if row["identity_projection"]["query_to_edge"]
        and all(
            query["source_triangle_ids"]
            for query in row["identity_projection"]["query_to_edge"]
        )
    ]

    receipt_source = (
        ROOT / PATHS["goal5835_receipt_source"]
    ).read_text(encoding="utf-8", errors="strict")
    fixture_source = (
        ROOT / PATHS["goal5835_fixture_source"]
    ).read_text(encoding="utf-8", errors="strict")
    receipt_direct_calls = _direct_call_names(receipt_source)
    fixture_direct_calls = _direct_call_names(fixture_source)
    permissive = SweptSphereSegment(
        sphere_id=1.5,
        path_segment_id=2.5,
        start=(0, 0, 0),
        end=(1, 0, 0),
        radius=0.25,
    )
    duplicate_probe = _duplicate_triangle_direction_probe()
    malformed_probe = _malformed_output_probe(piecewise.problem)

    author_labels = {
        anchor["label"]
        for row in a1_authority["author_source"]["locators"]
        for anchor in row["anchors"]
    }
    required_author_labels = {
        "directed_edge_set",
        "forward_loop_edge_emission",
        "reverse_loop_edge_emission",
        "loop_selects_directed_edges",
        "ccd_benchmark_enables_loop_edges",
        "one_sided_directed_edge_raygen",
    }
    if not required_author_labels <= author_labels:
        raise StrictAuditError("AUTHOR_DIRECTION_CALL_CHAIN_INCOMPLETE")

    findings = [
        {
            "id": "P1-G5835-CLAIM-SCOPE",
            "severity": "P1",
            "status": "OPEN_CLAIM_NARROWING_REQUIRED",
            "finding": (
                "Goal5835 validly binds app-shaped objects to inherited true-OptiX "
                "fixture bytes, but its evidence runner never executes the app front "
                "door or constructs a positive mesh/trajectory scene. The supportable "
                "class is bounded app-semantic projection, not executed paper app."
            ),
        },
        {
            "id": "P2-G5835-NO-POSITIVE-MESH",
            "severity": "P2",
            "status": "OPEN",
            "finding": (
                "No positive registered row reconstructs a complete triangle or mesh; "
                "the only complete-triangle row is the intentional miss boundary."
            ),
        },
        {
            "id": "P2-G5835-SYNTHETIC-SPHERE-IDENTITY",
            "severity": "P2",
            "status": "OPEN",
            "finding": (
                "The frozen fixture adapter assigns sphere_id=primitive_index. The "
                "connected piecewise-linear pair is therefore labelled as two spheres, "
                "and trajectory_to_swept_segments is not used by the evidence runner."
            ),
        },
        {
            "id": "P2-G5835-OUTPUT-FAIL-CLOSED",
            "severity": "P2",
            "status": "OPEN",
            "finding": (
                "execute_registered_problem accepts a result whose bit count differs "
                "from the edge count and whose collision value differs from OR(bits)."
            ),
        },
        {
            "id": "P2-G5835-DUPLICATE-TRIANGLE-DIRECTION",
            "severity": "P2",
            "status": "OPEN",
            "finding": (
                "Duplicate triangle IDs are accepted; stable sorting then preserves "
                "caller order, so an oppositely oriented shared edge changes direction "
                "when input order changes. Direction is predicate-significant here."
            ),
        },
        {
            "id": "P2-G5835-PATH-DEPENDENT-RECEIPT",
            "severity": "P2",
            "status": "KNOWN_HISTORICAL_DEFECT",
            "finding": (
                "The receipt serializes absolute source paths. Mac regeneration is "
                "scientifically identical after removing path fields but not byte "
                "identical to the frozen Windows result."
            ),
        },
        {
            "id": "P3-G5835-PERMISSIVE-ID-TYPES",
            "severity": "P3",
            "status": "OPEN_NON_LOAD_BEARING",
            "finding": (
                "SweptSphereSegment accepts non-integral numeric IDs inside the u32 "
                "range; path IDs fail later at the physical input, while sphere IDs "
                "can "
                "remain in app-only provenance."
            ),
        },
        {
            "id": "P2-G5836-HUMAN-SEMANTIC-STEP",
            "severity": "P2",
            "status": "DISCLOSED_REVIEW_LIMIT",
            "finding": (
                "A1 mechanically binds source bytes and anchors, but its semantic "
                "classification is a human-reviewed conclusion encoded as a constant; "
                "the hostile tests enforce custody and policy, not a graph theorem or "
                "mechanical PDF semantic extraction."
            ),
        },
    ]

    paper_source = (
        ROOT / PATHS["paper_main"]
    ).read_text(encoding="utf-8", errors="strict").lower()
    document = {
        "schema": "rtdl.goal5835_goal5836.strict_audit.v1",
        "date": "2026-09-01",
        "scope": "INTERNAL_HOSTILE_SELF_AUDIT__NO_NEW_GPU_OR_TIMING",
        "review_state": {
            "review_type": "INTERNAL_HOSTILE_SELF_AUDIT",
            "external_review_requested": False,
            "external_review_count": 0,
            "external_review_status": (
                "DEFERRED_BY_OWNER_UNTIL_RETURN_FROM_TRAVEL"
            ),
            "consensus_claimed": False,
        },
        "historical_inputs": identities,
        "verification": {
            "goal5836_preaction_verified": bool(preaction_authority),
            "goal5836_a0_verified": bool(a0_authority),
            "goal5836_a1_verified": bool(a1_authority),
            "goal5835_result_equals_recount_bytes": True,
            "goal5835_whole_document_regeneration_equal": (
                historical_result == regenerated
            ),
            "goal5835_semantic_regeneration_equal_ignoring_absolute_paths":
                semantic_regeneration_equal,
            "goal5833_to_goal5836_regression_expected_count": 148,
        },
        "goal5835": {
            "strict_classification": (
                "BOUNDED_APP_SEMANTIC_PROJECTION_WITH_INHERITED_TRUE_OPTIX_EVIDENCE"
            ),
            "executed_paper_app": False,
            "paper_app_status": "NOT_A_PAPER_APP",
            "new_goal5835_gpu_launch_count": 0,
            "inherited_b3_true_optix_launch_count": 33,
            "receipt_source_directly_calls_execute_registered_problem":
                "execute_registered_problem" in receipt_direct_calls,
            "receipt_source_directly_calls_trajectory_to_swept_segments":
                "trajectory_to_swept_segments" in receipt_direct_calls,
            "receipt_source_directly_calls_deduplicate_triangle_edges":
                "deduplicate_triangle_edges" in receipt_direct_calls,
            "fixture_loader_calls_deduplicate_triangle_edges":
                "deduplicate_triangle_edges" in fixture_direct_calls,
            "fixture_loader_deduplication_scope": (
                "NEGATIVE_FACE_INTERIOR_BOUNDARY_RECONSTRUCTION_ONLY"
            ),
            "complete_mesh_rows": complete_mesh_rows,
            "positive_complete_mesh_rows": complete_mesh_positive_rows,
            "piecewise_connected": (
                piecewise.problem.swept_segments[0].end
                == piecewise.problem.swept_segments[1].start
            ),
            "piecewise_sphere_ids": [
                row.sphere_id for row in piecewise.problem.swept_segments
            ],
            "duplicate_triangle_direction_probe": duplicate_probe,
            "malformed_output_probe": malformed_probe,
            "permissive_id_probe": {
                "accepted": True,
                "sphere_id": permissive.sphere_id,
                "path_segment_id": permissive.path_segment_id,
            },
        },
        "goal5836": {
            "a1_classification": a1_authority["classification"],
            "a1_status": a1_authority["status"],
            "terminal_refusal_confirmed": True,
            "transaction_complete": True,
            "paper_app_promotion_succeeded": False,
            "core_reasoning_verdict": (
                "ACCEPT__PAPER_AND_AUTHOR_CALL_CHAIN_SUPPORT_MATERIAL_"
                "DIRECTION_AND_INSIDE_START_DIFFERENCE"
            ),
            "required_author_direction_labels_present": sorted(
                required_author_labels
            ),
            "paper_semantics_mechanically_reextracted": False,
            "author_or_rtdl_goal5836_execution_count": 0,
            "performance_timing_count": 0,
        },
        "cgo_manuscript_impact": {
            "audited_file": _identity("paper_main"),
            "goal5835_literal_present": "goal5835" in paper_source,
            "goal5836_literal_present": "goal5836" in paper_source,
            "sui_is_used_as_related_work_problem_inventory": (
                "sui2024hardwareacceleratedrt" in paper_source
            ),
            "negative_goal5836_result_should_be_added_as_experiment": False,
        },
        "findings": findings,
        "verdict": {
            "p0": 0,
            "p1": 1,
            "p2": 6,
            "p3": 1,
            "goal5835": (
                "ACCEPT_ONLY_AFTER_CLAIM_NARROWING__NOT_AN_EXECUTED_PAPER_APP"
            ),
            "goal5836": (
                "ACCEPT_TERMINAL_A1_NEGATIVE_OUTCOME__NO_A2__NO_POD_REQUIRED"
            ),
        },
        "claim_boundary": {
            "goal5835_may_be_called_full_rtccd": False,
            "goal5835_may_be_called_paper_reproduction": False,
            "goal5835_may_be_called_executed_app_front_door_result": False,
            "goal5835_may_be_called_bounded_app_semantic_projection": True,
            "goal5836_may_be_called_successful_paper_app": False,
            "goal5836_may_be_called_completed_negative_fidelity_transaction": True,
            "new_performance_claim_authorized": False,
        },
        "next_action": {
            "pod_required_for_this_audit": False,
            "external_review_required_now": False,
            "external_review_debt_recorded": True,
            "historical_goal5835_or_goal5836_bytes_may_be_rewritten": False,
            "safe_local_work": [
                "publish_current_status_and_claim_narrowing",
                "preserve hostile counterexamples as tests",
                "design_separate_successor_preaction_if_owner_wants_repair",
            ],
            "future_successor_requires": [
                "app_neutral_directed_orientation_or_connectivity_contract",
                "real_trajectory_and_positive_complete_mesh_fixture",
                "fail_closed_app_result_validation",
                "same_input_author_rtdl_oracle_execution_after_freeze",
                "modern_rtx_pod_only_after_local_gate_passes",
            ],
        },
        "strict_audit_authority_sha256": "",
    }
    document["strict_audit_authority_sha256"] = _seal(document)
    validate_policy(document)
    return document


def validate_policy(document: dict[str, Any]) -> None:
    if document.get("strict_audit_authority_sha256") != _seal(document):
        raise StrictAuditError("AUDIT_SEAL_MISMATCH")
    findings = document.get("findings")
    if not isinstance(findings, list) or {
            row.get("id") for row in findings
    } != EXPECTED_FINDINGS:
        raise StrictAuditError("FINDING_SET_MISMATCH")
    if document.get("verdict") != {
        "p0": 0,
        "p1": 1,
        "p2": 6,
        "p3": 1,
        "goal5835": "ACCEPT_ONLY_AFTER_CLAIM_NARROWING__NOT_AN_EXECUTED_PAPER_APP",
        "goal5836": "ACCEPT_TERMINAL_A1_NEGATIVE_OUTCOME__NO_A2__NO_POD_REQUIRED",
    }:
        raise StrictAuditError("VERDICT_MISMATCH")
    if document.get("review_state") != {
        "review_type": "INTERNAL_HOSTILE_SELF_AUDIT",
        "external_review_requested": False,
        "external_review_count": 0,
        "external_review_status": "DEFERRED_BY_OWNER_UNTIL_RETURN_FROM_TRAVEL",
        "consensus_claimed": False,
    }:
        raise StrictAuditError("REVIEW_STATE_MISMATCH")
    goal5835 = document.get("goal5835", {})
    if (
        goal5835.get("executed_paper_app") is not False
        or goal5835.get("positive_complete_mesh_rows") != []
        or goal5835.get(
            "receipt_source_directly_calls_execute_registered_problem"
        ) is not False
        or goal5835.get(
            "receipt_source_directly_calls_trajectory_to_swept_segments"
        ) is not False
        or goal5835.get(
            "receipt_source_directly_calls_deduplicate_triangle_edges"
        ) is not False
        or goal5835.get(
            "fixture_loader_calls_deduplicate_triangle_edges"
        ) is not True
        or goal5835.get("fixture_loader_deduplication_scope")
        != "NEGATIVE_FACE_INTERIOR_BOUNDARY_RECONSTRUCTION_ONLY"
        or goal5835.get("piecewise_sphere_ids") != [0, 1]
        or goal5835.get("duplicate_triangle_direction_probe", {}).get(
            "input_order_invariant"
        ) is not False
        or goal5835.get("malformed_output_probe", {}).get(
            "malformed_output_rejected"
        ) is not False
    ):
        raise StrictAuditError("GOAL5835_COUNTEREVIDENCE_MISMATCH")
    goal5836 = document.get("goal5836", {})
    if (
        goal5836.get("a1_classification") != "MATERIAL_PREDICATE_DIFFERENCE"
        or goal5836.get("terminal_refusal_confirmed") is not True
        or goal5836.get("paper_app_promotion_succeeded") is not False
        or goal5836.get("author_or_rtdl_goal5836_execution_count") != 0
    ):
        raise StrictAuditError("GOAL5836_VERDICT_MISMATCH")
    if document.get("next_action", {}).get(
            "pod_required_for_this_audit") is not False:
        raise StrictAuditError("POD_REQUIREMENT_MISMATCH")
    if (
        document.get("next_action", {}).get("external_review_required_now")
        is not False
        or document.get("next_action", {}).get(
            "external_review_debt_recorded") is not True
    ):
        raise StrictAuditError("EXTERNAL_REVIEW_BOUNDARY_MISMATCH")


def verify_stored(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    path = output / AUTHORITY_FILENAME
    observed = json.loads(path.read_text(encoding="ascii", errors="strict"))
    expected = build_authority()
    if observed != expected:
        raise StrictAuditError("STORED_AUDIT_EXACT_DOCUMENT_MISMATCH")
    validate_policy(observed)
    return observed


def write_authority(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    path = output / AUTHORITY_FILENAME
    if output.exists() or path.exists():
        raise FileExistsError("strict audit output already exists")
    document = build_authority()
    output.mkdir(parents=True)
    path.write_bytes(_pretty(document))
    return verify_stored(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-stored", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    document = (
        verify_stored(args.output)
        if args.verify_stored
        else write_authority(args.output)
    )
    print(json.dumps({
        "status": "PASS__GOAL5835_GOAL5836_STRICT_AUDIT",
        "goal5835": document["verdict"]["goal5835"],
        "goal5836": document["verdict"]["goal5836"],
        "p0": document["verdict"]["p0"],
        "p1": document["verdict"]["p1"],
        "p2": document["verdict"]["p2"],
        "p3": document["verdict"]["p3"],
        "pod_required": document["next_action"]["pod_required_for_this_audit"],
        "review_type": document["review_state"]["review_type"],
        "authority_seal": document["strict_audit_authority_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
