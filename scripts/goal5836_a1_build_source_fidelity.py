#!/usr/bin/env python3
"""Build and verify the terminal Goal5836 A1 source-fidelity authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import goal5836_a0_build_source_acquisition as a0


OUTPUT_RELATIVE = (
    "history/internal_docs/goal5836_a1_source_fidelity_20260901"
)
DEFAULT_OUTPUT = ROOT / OUTPUT_RELATIVE
AUTHORITY_FILENAME = "SOURCE_FIDELITY_AUTHORITY.json"
A0_OUTPUT = a0.DEFAULT_OUTPUT
A0_AUTHORITY_RELATIVE = (
    "history/internal_docs/goal5836_a0_source_acquisition_20260901/"
    "SOURCE_ACQUISITION_AUTHORITY.json"
)
A0_AUTHORITY_PIN = (
    7090,
    "5d18d5736be47288e6867d29df93a05bc2f7a81462101e563d65f88c5d236bef",
)
OWNER_AUTHORIZATION_RELATIVE = (
    "history/internal_docs/goal5836_a1_owner_authorization_20260901.md"
)
OWNER_AUTHORIZATION_PIN = (
    1189,
    "066dbd5ea12182f6eda1936ade2ba3b1dc0be2a019b7e1d9989f524d1a9efa47",
)
GOAL5835_RESULT_RELATIVE = (
    "history/internal_docs/"
    "goal5835_sui_derived_edge_crossing_mapping_result_20260830.json"
)
GOAL5835_RESULT_PIN = (
    15642,
    "ae370da1ca5ac96562d0956438e7c6c8eee39fddf2d9894953db8e956c47ccff",
)
GOAL5835_CORE_RELATIVE = (
    "case_studies/sui_derived_edge_crossing_core/"
    "bounded_piecewise_linear_core.py"
)
GOAL5835_CORE_PIN = (
    9698,
    "65e61185117a9cb052a1b4a6c29cc83346f9405911231784b7f2cd8b5eb0952f",
)
GOAL5835_README_RELATIVE = (
    "case_studies/sui_derived_edge_crossing_core/README.md"
)
GOAL5835_README_PIN = (
    2549,
    "b8ff0817518785635d005665601b7590664e01a1854a860d39ea604e290abdbd",
)
AUTHOR_COMMIT = a0.AUTHOR_COMMIT
AUTHOR_PREFIX = f"RTCollisionDetection-{AUTHOR_COMMIT}"
DOMAIN = b"rtdl.goal5836.a1.source_fidelity_authority.v1\0"

AUTHOR_FILES = (
    "RTCD/Meshes/mesh.h",
    "RTCD/CollisionScenes/obstacle.h",
    "RTCD/Benchmark/Curve/benchmark.cpp",
    "RTCD/Robot/batchCurveRobot.h",
    "RTCD/CollisionDetector/CCCuda.cu",
    "RTCD/CollisionDetector/CollisionDetector.h",
    "RTCD/CollisionDetector/Test/testCollisionCheckerCurve.cpp",
)

AUTHOR_ANCHORS = (
    {
        "path": "RTCD/Meshes/mesh.h",
        "label": "directed_edge_set",
        "text": "std::unordered_set<int2> ordered_edges;",
        "occurrences": 1,
    },
    {
        "path": "RTCD/Meshes/mesh.h",
        "label": "forward_loop_edge_emission",
        "text": (
            "mesh.loopEdgeIndices.push_back(make_int2("
            "forwardLoop[i], forwardLoop[i + 1]));"
        ),
        "occurrences": 1,
    },
    {
        "path": "RTCD/Meshes/mesh.h",
        "label": "reverse_loop_edge_emission",
        "text": (
            "mesh.loopEdgeIndices.push_back(make_int2("
            "forwardLoop[i + 1], forwardLoop[i]));"
        ),
        "occurrences": 1,
    },
    {
        "path": "RTCD/CollisionScenes/obstacle.h",
        "label": "loop_selects_directed_edges",
        "text": (
            "std::vector<int2>& edgeIndices = loop ? "
            "mesh.loopEdgeIndices : mesh.uniqueEdgeIndices;"
        ),
        "occurrences": 2,
    },
    {
        "path": "RTCD/Benchmark/Curve/benchmark.cpp",
        "label": "ccd_benchmark_enables_loop_edges",
        "text": (
            "std::shared_ptr<scene> s     = buildSharedScene(true); "
            "// curve scene, loop edge"
        ),
        "occurrences": 1,
    },
    {
        "path": "RTCD/Robot/batchCurveRobot.h",
        "label": "linear_curve_segments_follow_pose_samples",
        "text": "nSegsPerCur = nCPtsPerCur - 1;",
        "occurrences": 1,
    },
    {
        "path": "RTCD/Robot/batchCurveRobot.h",
        "label": "sphere_radius_copied_to_curve_widths",
        "text": "sphereRadiusTemplate[i]);",
        "occurrences": 1,
    },
    {
        "path": "RTCD/Robot/batchCurveRobot.h",
        "label": "round_linear_primitive",
        "text": (
            "Base::buildInput.curveArray.curveType = "
            "OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR;"
        ),
        "occurrences": 1,
    },
    {
        "path": "RTCD/Robot/batchCurveRobot.h",
        "label": "curve_width_buffer",
        "text": (
            "Base::buildInput.curveArray.widthBuffers         = "
            "&curveCFG.curveRadiusBufferPtr;"
        ),
        "occurrences": 1,
    },
    {
        "path": "RTCD/Robot/batchCurveRobot.h",
        "label": "round_endcaps_enabled",
        "text": "Base::buildInput.curveArray.endcapFlags          = 1;",
        "occurrences": 1,
    },
    {
        "path": "RTCD/CollisionDetector/CCCuda.cu",
        "label": "hit_count_reduced_by_pose",
        "text": (
            "atomicAdd((int*) optixLaunchParams.hitBuffer + "
            "optixLaunchParams.mesh.primIdxToPoseIdx[primID], 1);"
        ),
        "occurrences": 2,
    },
    {
        "path": "RTCD/CollisionDetector/CCCuda.cu",
        "label": "finite_edge_ray_origin",
        "text": (
            "const float3 origin = "
            "optixLaunchParams.verticesBuffer[idx * 2];"
        ),
        "occurrences": 1,
    },
    {
        "path": "RTCD/CollisionDetector/CollisionDetector.h",
        "label": "one_sided_directed_edge_raygen",
        "text": (
            "pgDesc.raygen.entryFunctionName = "
            "\"__raygen__oneside\";"
        ),
        "occurrences": 1,
    },
    {
        "path": "RTCD/CollisionDetector/CollisionDetector.h",
        "label": "round_linear_builtin_endcaps",
        "text": "builtinISOptions.curveEndcapFlags    = 1;",
        "occurrences": 3,
    },
    {
        "path": (
            "RTCD/CollisionDetector/Test/"
            "testCollisionCheckerCurve.cpp"
        ),
        "label": "piecewise_linear_selected_type",
        "text": "inline constexpr LinkType TYPE    = LinkType::LINEAR_CURVE;",
        "occurrences": 1,
    },
    {
        "path": (
            "RTCD/CollisionDetector/Test/"
            "testCollisionCheckerCurve.cpp"
        ),
        "label": "quadratic_endpoint_pose_composition",
        "text": "if constexpr (TYPE == LinkType::QUADRATIC_CURVE) {",
        "occurrences": 1,
    },
    {
        "path": (
            "RTCD/CollisionDetector/Test/"
            "testCollisionCheckerCurve.cpp"
        ),
        "label": "positive_hit_count_is_collision",
        "text": "if (result[i] > 0 && result_gt[i] == 0)",
        "occurrences": 1,
    },
)

GOAL5835_ANCHORS = (
    {
        "path": GOAL5835_CORE_RELATIVE,
        "label": "first_occurrence_fixes_arbitrary_direction",
        "text": "the first occurrence fixes query direction. Deduplication",
        "occurrences": 1,
    },
    {
        "path": GOAL5835_CORE_RELATIVE,
        "label": "first_edge_occurrence_is_preserved",
        "text": "if key not in rows:",
        "occurrences": 1,
    },
    {
        "path": GOAL5835_README_RELATIVE,
        "label": "initial_overlap_is_excluded",
        "text": (
            "This is **not** complete RT-CCD. It excludes initial "
            "overlap/start-inside,"
        ),
        "occurrences": 1,
    },
    {
        "path": GOAL5835_README_RELATIVE,
        "label": "face_interior_is_excluded",
        "text": "edge crossing. It exposes neither time of impact nor collided",
        "occurrences": 1,
    },
)

IMPLEMENTATION_PATHS = (
    "scripts/goal5836_a1_build_source_fidelity.py",
    "tests/goal5836_a1_source_fidelity_test.py",
)

AUTHORIZATION = {
    "a0_completed": True,
    "a1_owner_authorized": True,
    "a1_static_inspection_completed": True,
    "a1_authorization_consumed": True,
    "a2_input_freeze_authorized": False,
    "a3_route_materialization_authorized": False,
    "a4_modern_rtx_execution_authorized": False,
    "a5_paper_app_decision_authorized": False,
    "author_build_or_execution_authorized": False,
    "product_or_case_study_mutation_authorized": False,
    "pod_or_gpu_authorized": False,
    "timing_or_performance_authorized": False,
    "external_review_authorized": False,
    "public_claim_authorized": False,
}

OBSERVATION = {
    "paper_method_semantics_inspected": True,
    "author_source_semantics_inspected": True,
    "source_fidelity_classification_made": True,
    "author_program_output_inspected": False,
    "author_build_count": 0,
    "author_execution_count": 0,
    "rtdl_goal5836_execution_count": 0,
    "input_freeze_count": 0,
    "route_materialization_count": 0,
    "gpu_worker_count": 0,
    "timing_count": 0,
    "performance_result_count": 0,
    "product_or_case_study_mutation_count": 0,
    "external_review_count": 0,
}

CLASSIFICATION = "MATERIAL_PREDICATE_DIFFERENCE"
STATUS = "TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE__A2_NOT_REACHABLE"


class A1Error(RuntimeError):
    """Raised when A1 custody or the preregistered policy is violated."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _pretty_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii") + b"\n"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seal(document: dict[str, Any]) -> str:
    payload = dict(document)
    payload["source_fidelity_authority_sha256"] = ""
    return hashlib.sha256(DOMAIN + canonical_json_bytes(payload)).hexdigest()


def _identity(relative: str) -> dict[str, Any]:
    logical = PurePosixPath(relative)
    if logical.is_absolute() or ".." in logical.parts:
        raise A1Error(f"NON_PORTABLE_IDENTITY_PATH:{relative}")
    data = (ROOT / relative).read_bytes()
    return {
        "path": logical.as_posix(),
        "bytes": len(data),
        "sha256": _sha256(data),
    }


def _verify_pin(relative: str, expected: tuple[int, str]) -> None:
    row = _identity(relative)
    if (row["bytes"], row["sha256"]) != expected:
        raise A1Error(f"STATIC_PIN_MISMATCH:{relative}")


def _load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="ascii", errors="strict"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {value}")
        ),
    )


def _line_locator(data: bytes, spec: dict[str, Any]) -> dict[str, Any]:
    text = data.decode("utf-8", errors="strict")
    needle = spec["text"]
    line_numbers = [
        index
        for index, line in enumerate(text.splitlines(), 1)
        if needle in line
    ]
    if len(line_numbers) != spec["occurrences"]:
        raise A1Error(
            f"SOURCE_ANCHOR_COUNT:{spec['path']}:{spec['label']}:"
            f"{len(line_numbers)}"
        )
    return {
        "label": spec["label"],
        "line_numbers": line_numbers,
        "occurrence_count": len(line_numbers),
        "anchor_sha256": _sha256(needle.encode("utf-8")),
    }


def _verified_author_sources() -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    authority = a0.verify_stored(A0_OUTPUT)
    authority_bytes = (ROOT / A0_AUTHORITY_RELATIVE).read_bytes()
    if (len(authority_bytes), _sha256(authority_bytes)) != A0_AUTHORITY_PIN:
        raise A1Error("A0_AUTHORITY_PIN_MISMATCH")
    if authority["status"] != "PASS__EXACT_SOURCE_BYTES_ACQUIRED_AND_HASHED__A1_LOCKED":
        raise A1Error("A0_DID_NOT_PASS")

    manifest = _load_json(A0_OUTPUT / "AUTHOR_SELECTED_SOURCE_MANIFEST.json")
    inventory = _load_json(A0_OUTPUT / "AUTHOR_SOURCE_TREE_INVENTORY.json")
    manifest_rows = {row["path"]: row for row in manifest["rows"]}
    inventory_rows = {row["path"]: row for row in inventory["rows"]}
    if manifest["commit"] != AUTHOR_COMMIT or manifest["archive_prefix"] != AUTHOR_PREFIX:
        raise A1Error("AUTHOR_SOURCE_PREFIX_OR_COMMIT_MISMATCH")
    if set(manifest_rows) - set(inventory_rows):
        raise A1Error("SELECTED_SOURCE_NOT_IN_COMPLETE_INVENTORY")

    archive_path = A0_OUTPUT / "AUTHOR_SELECTED_SOURCE.tar.gz"
    sources: dict[str, bytes] = {}
    observed_names: list[str] = []
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive.getmembers():
            logical = PurePosixPath(member.name)
            if (
                logical.is_absolute()
                or ".." in logical.parts
                or not member.isfile()
                or member.name in observed_names
            ):
                raise A1Error(f"UNSAFE_AUTHOR_CAPSULE_MEMBER:{member.name}")
            observed_names.append(member.name)
            expected_prefix = f"{AUTHOR_PREFIX}/"
            if not member.name.startswith(expected_prefix):
                raise A1Error(f"AUTHOR_CAPSULE_PREFIX_MISMATCH:{member.name}")
            relative = member.name[len(expected_prefix):]
            row = manifest_rows.get(relative)
            stream = archive.extractfile(member)
            if row is None or stream is None:
                raise A1Error(f"UNREGISTERED_AUTHOR_CAPSULE_MEMBER:{member.name}")
            data = stream.read()
            if (
                len(data) != row["bytes"]
                or _sha256(data) != row["sha256"]
                or a0._git_oid("blob", data) != row["git_oid_sha1"]
                or row != inventory_rows[relative]
            ):
                raise A1Error(f"AUTHOR_CAPSULE_BLOB_MISMATCH:{relative}")
            sources[relative] = data
    expected_names = [f"{AUTHOR_PREFIX}/{row['path']}" for row in manifest["rows"]]
    if observed_names != expected_names:
        raise A1Error("AUTHOR_CAPSULE_MEMBER_ORDER_OR_SET_MISMATCH")
    if any(path not in sources for path in AUTHOR_FILES):
        raise A1Error("REQUIRED_A1_AUTHOR_SOURCE_MISSING")
    identities = [
        {
            "path": path,
            "bytes": manifest_rows[path]["bytes"],
            "sha256": manifest_rows[path]["sha256"],
            "git_oid_sha1": manifest_rows[path]["git_oid_sha1"],
        }
        for path in AUTHOR_FILES
    ]
    return sources, identities


def _group_author_locators(sources: dict[str, bytes]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {path: [] for path in AUTHOR_FILES}
    for spec in AUTHOR_ANCHORS:
        grouped[spec["path"]].append(_line_locator(sources[spec["path"]], spec))
    return [
        {"path": path, "anchors": grouped[path]}
        for path in AUTHOR_FILES
        if grouped[path]
    ]


def _goal5835_locators() -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for spec in GOAL5835_ANCHORS:
        data = (ROOT / spec["path"]).read_bytes()
        grouped.setdefault(spec["path"], []).append(_line_locator(data, spec))
    return [
        {"path": path, "anchors": anchors}
        for path, anchors in sorted(grouped.items())
    ]


def build_authority() -> dict[str, Any]:
    _verify_pin(A0_AUTHORITY_RELATIVE, A0_AUTHORITY_PIN)
    _verify_pin(OWNER_AUTHORIZATION_RELATIVE, OWNER_AUTHORIZATION_PIN)
    _verify_pin(GOAL5835_RESULT_RELATIVE, GOAL5835_RESULT_PIN)
    _verify_pin(GOAL5835_CORE_RELATIVE, GOAL5835_CORE_PIN)
    _verify_pin(GOAL5835_README_RELATIVE, GOAL5835_README_PIN)
    sources, author_identities = _verified_author_sources()

    document: dict[str, Any] = {
        "schema": "rtdl.goal5836.a1.source_fidelity_authority.v1",
        "date": "2026-09-01",
        "goal": "5836-A1",
        "status": STATUS,
        "classification": CLASSIFICATION,
        "authorization": AUTHORIZATION,
        "a1_observation": OBSERVATION,
        "predecessors": [
            _identity(A0_AUTHORITY_RELATIVE),
            _identity(OWNER_AUTHORIZATION_RELATIVE),
            _identity(GOAL5835_RESULT_RELATIVE),
            _identity(GOAL5835_CORE_RELATIVE),
            _identity(GOAL5835_README_RELATIVE),
        ],
        "paper_evidence": {
            "identity_sha256": a0.PAPER_SHA256,
            "identity_bytes": a0.PAPER_BYTES,
            "kind": (
                "OFFICIAL_ARXIV_V2_AUTHOR_SUBMITTED_REVISION__"
                "NOT_IEEE_PUBLISHER_PDF"
            ),
            "semantic_locators": [
                {
                    "pdf_page": 5,
                    "section": "III-C Continuous Collision Detection",
                    "supports": [
                        "constant-radius round curve equals swept sphere",
                        "piecewise-linear sphere centers interpolate between poses",
                        "strongly-connected directed obstacle edges address inside starts",
                    ],
                },
                {
                    "pdf_page": 7,
                    "section": "V-A.2 RT-CCD Accuracy",
                    "supports": [
                        "RT-CCD detects swept-sphere collisions with mesh edges, not faces"
                    ],
                },
                {
                    "pdf_page": 10,
                    "section": "Algorithm 2 and Appendix D",
                    "supports": [
                        "directed graph is constructed to preserve CCD correctness"
                    ],
                },
            ],
        },
        "author_source": {
            "repository": a0.AUTHOR_REPOSITORY,
            "commit": AUTHOR_COMMIT,
            "root_tree_git_oid_sha1": a0.AUTHOR_ROOT_TREE,
            "selection_basis": (
                "A1_REQUIRED_SEMANTIC_CALL_CHAIN__SELECTED_BEFORE_ANY_"
                "GOAL5836_PROGRAM_OUTPUT"
            ),
            "selected_files": author_identities,
            "locators": _group_author_locators(sources),
        },
        "goal5835_source": {
            "implemented_predicate": (
                "OR_over_registered_obstacle_edges_of_OR_over_"
                "swept_sphere_capsules"
            ),
            "locators": _goal5835_locators(),
        },
        "semantic_classification": [
            {
                "dimension": "piecewise_linear_swept_sphere_representation",
                "author_semantics": (
                    "sphere centers at successive poses form round-linear curves"
                ),
                "goal5835_semantics": (
                    "each sphere path segment forms one round-linear capsule"
                ),
                "decision": "MATCH",
            },
            {
                "dimension": "constant_radius_width_and_linear_endcaps",
                "author_semantics": (
                    "sphere radius is copied to curve widths and round endcaps are enabled"
                ),
                "goal5835_semantics": (
                    "constant positive radius is assigned at both segment endpoints"
                ),
                "decision": "MATCH",
            },
            {
                "dimension": "finite_edge_hit_boolean_reduction",
                "author_semantics": (
                    "finite obstacle-edge rays increment per-trajectory hit counts; count>0 is collision"
                ),
                "goal5835_semantics": (
                    "per-edge hit bits are OR-reduced to a collision Boolean"
                ),
                "decision": "MATCH_AT_BOOLEAN_PREDICATE_LEVEL",
            },
            {
                "dimension": "face_interior_only_collision",
                "author_semantics": (
                    "RT-CCD intentionally detects mesh-edge collisions rather than face-only collisions"
                ),
                "goal5835_semantics": (
                    "face-interior-only collision without edge contact is a visible miss boundary"
                ),
                "decision": "MATCH_LIMITATION",
            },
            {
                "dimension": "obstacle_edge_direction_contract",
                "author_semantics": (
                    "actual curve benchmark uses a strongly-connected directed edge graph, including selected bidirectional edges"
                ),
                "goal5835_semantics": (
                    "shared edges are deduplicated and the first sorted triangle occurrence fixes one arbitrary direction"
                ),
                "decision": "MATERIAL_PREDICATE_DIFFERENCE",
            },
            {
                "dimension": "inside_start_and_initial_overlap_coverage",
                "author_semantics": (
                    "directed connectivity is required to recover collisions when an edge vertex begins inside a hollow OptiX curve"
                ),
                "goal5835_semantics": (
                    "start-inside and initial overlap are explicitly excluded and no connectivity invariant is enforced"
                ),
                "decision": "MATERIAL_PREDICATE_DIFFERENCE",
            },
            {
                "dimension": "discrete_endpoint_pose_composition",
                "author_semantics": (
                    "linear curves use round endcaps; quadratic test results separately add endpoint-pose results"
                ),
                "goal5835_semantics": (
                    "selected piecewise-linear route uses round endcaps and claims no quadratic route"
                ),
                "decision": "MATCH_FOR_SELECTED_LINEAR_SUBPATH_ONLY",
            },
        ],
        "classification_reason": (
            "The author benchmark's directed-connectivity invariant changes "
            "inside-start collision coverage. Goal5835 neither preserves that "
            "invariant nor includes initial-overlap behavior, so the selected "
            "mapping is not source-faithful even though its ordinary crossing, "
            "radius, endcap, face-limit, and Boolean semantics align."
        ),
        "terminal_transition": {
            "preaction_outcome": (
                "TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE"
            ),
            "a2_reachable": False,
            "a3_reachable": False,
            "a4_reachable": False,
            "a5_reachable": False,
            "next_owner_gate": "NONE__A1_TERMINAL_NEGATIVE_OUTCOME",
            "input_replacement_allowed": False,
            "predicate_repair_inside_goal5836_allowed": False,
        },
        "goal_completion": {
            "goal5836_transaction_complete": True,
            "successful_promotion_path_complete": False,
            "terminal_stage": "A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION",
            "scientific_outcome": (
                "SOURCE_FIDELITY_MATERIAL_DIFFERENCE__NO_PAPER_APP_PROMOTION"
            ),
        },
        "claim_boundary": {
            "paper_app_status": "NOT_A_PAPER_APP",
            "source_relation": (
                "SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES__"
                "A1_MATERIAL_PREDICATE_DIFFERENCE"
            ),
            "goal5835_scope_preserved": True,
            "goal5836_functional_result_claimed": False,
            "paper_app_claimed": False,
            "performance_claimed": False,
            "complete_rtccd_claimed": False,
            "generalization_exam_count": 0,
        },
        "implementation_and_tests": [
            _identity(path) for path in IMPLEMENTATION_PATHS
        ],
        "source_fidelity_authority_sha256": "",
    }
    document["source_fidelity_authority_sha256"] = _seal(document)
    validate_policy(document)
    return document


def validate_policy(document: dict[str, Any]) -> None:
    if document.get("schema") != "rtdl.goal5836.a1.source_fidelity_authority.v1":
        raise A1Error("SCHEMA_MISMATCH")
    if document.get("source_fidelity_authority_sha256") != _seal(document):
        raise A1Error("AUTHORITY_SEAL_MISMATCH")
    if document.get("status") != STATUS or document.get("classification") != CLASSIFICATION:
        raise A1Error("CLASSIFICATION_OR_STATUS_MISMATCH")
    if document.get("authorization") != AUTHORIZATION:
        raise A1Error("AUTHORIZATION_DOCUMENT_MISMATCH")
    if document.get("a1_observation") != OBSERVATION:
        raise A1Error("A1_OBSERVATION_MISMATCH")
    matrix = document.get("semantic_classification")
    if not isinstance(matrix, list) or len(matrix) != 7:
        raise A1Error("CLASSIFICATION_MATRIX_SHAPE")
    material = {
        row.get("dimension")
        for row in matrix
        if row.get("decision") == "MATERIAL_PREDICATE_DIFFERENCE"
    }
    if material != {
        "obstacle_edge_direction_contract",
        "inside_start_and_initial_overlap_coverage",
    }:
        raise A1Error("MATERIAL_DIFFERENCE_ROWS_MISMATCH")
    transition = document.get("terminal_transition", {})
    if transition != {
        "preaction_outcome": "TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE",
        "a2_reachable": False,
        "a3_reachable": False,
        "a4_reachable": False,
        "a5_reachable": False,
        "next_owner_gate": "NONE__A1_TERMINAL_NEGATIVE_OUTCOME",
        "input_replacement_allowed": False,
        "predicate_repair_inside_goal5836_allowed": False,
    }:
        raise A1Error("TERMINAL_TRANSITION_MISMATCH")
    completion = document.get("goal_completion", {})
    if (
        completion.get("goal5836_transaction_complete") is not True
        or completion.get("successful_promotion_path_complete") is not False
        or completion.get("terminal_stage")
        != "A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION"
    ):
        raise A1Error("GOAL_COMPLETION_MISMATCH")
    claim = document.get("claim_boundary", {})
    if (
        claim.get("paper_app_status") != "NOT_A_PAPER_APP"
        or claim.get("goal5835_scope_preserved") is not True
        or claim.get("paper_app_claimed") is not False
        or claim.get("performance_claimed") is not False
        or claim.get("complete_rtccd_claimed") is not False
        or claim.get("generalization_exam_count") != 0
    ):
        raise A1Error("CLAIM_BOUNDARY_MISMATCH")
    for row in document.get("predecessors", []):
        logical = PurePosixPath(row.get("path", ""))
        if logical.is_absolute() or ".." in logical.parts:
            raise A1Error("NON_PORTABLE_PREDECESSOR_PATH")
    selected = document.get("author_source", {}).get("selected_files", [])
    if [row.get("path") for row in selected] != list(AUTHOR_FILES):
        raise A1Error("AUTHOR_SOURCE_SELECTION_MISMATCH")


def verify_stored(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    path = output / AUTHORITY_FILENAME
    observed = _load_json(path)
    expected = build_authority()
    if observed != expected or path.read_bytes() != _pretty_json_bytes(expected):
        raise A1Error("STORED_AUTHORITY_REBUILD_MISMATCH")
    validate_policy(observed)
    return observed


def write_authority(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    path = output / AUTHORITY_FILENAME
    if path.exists():
        raise A1Error("CREATE_ONLY_AUTHORITY_ALREADY_EXISTS")
    document = build_authority()
    path.write_bytes(_pretty_json_bytes(document))
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
        "status": document["status"],
        "classification": document["classification"],
        "authority_seal": document["source_fidelity_authority_sha256"],
        "goal5836_transaction_complete": document["goal_completion"][
            "goal5836_transaction_complete"
        ],
        "next_owner_gate": document["terminal_transition"]["next_owner_gate"],
        "worker_count": document["a1_observation"]["gpu_worker_count"],
        "timing_count": document["a1_observation"]["timing_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
