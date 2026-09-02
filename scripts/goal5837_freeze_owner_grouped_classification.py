#!/usr/bin/env python3
"""Freeze the narrow Goal5837 classification and its claim-source matrix.

This authority classifies already-produced successor evidence.  It does not
register a stable V4 protocol constructor, run a GPU, or upgrade any paper or
performance claim.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = (
    ROOT
    / "history/internal_docs/goal5837_owner_grouped_classification_20260902"
)
STORED_AUTHORITY = OUTPUT_DIR / "GOAL5837_AUTHORITY.json"
DOMAIN = b"rtdl.goal5837.owner_grouped_classification.v1\0"

INPUT_CHECKPOINT = "8180d754e7637670b502b17866be2a29ea1cc26f"
GPU_EXECUTION_CHECKPOINT = "7ec6b673b1da3dbe63ff2915e82d61f5302bf85c"
EXACT_CLASSIFICATION = (
    "ADDITIONAL_ROOT_EXPORTED_CLOSED_SUCCESSOR_ROUTE__"
    "NOT_STABLE_V4_FIXED_CONSTRUCTOR"
)
STABLE_CONSTRUCTORS = (
    "custom_aabb_bounded_relation_v1",
    "builtin_triangle_reduction_v1",
)
SUCCESSOR_EXPORTS = (
    "OwnerGroupedCurveQueryBatch",
    "OwnerGroupedCurveStaticInput",
    "PreparedCurveOwnerGroupedAnyHitProgram",
    "V4CurveTarget",
    "curve_owner_grouped_any_hit_source",
)
SUCCESSOR_LIFECYCLE = {
    "VerifiedCurveOwnerGroupedAnyHitSource": ("compile",),
    "VerifiedCurveOwnerGroupedAnyHitProgram": ("materialize",),
    "MaterializedCurveOwnerGroupedAnyHitProgram": ("prepare",),
    "PreparedCurveOwnerGroupedAnyHitProgram": ("execute", "close"),
}
APPLICATION_TERMS = ("collision", "trajectory", "robot", "pose", "rtccd")

HISTORICAL_INPUTS = {
    "goal5831_scope_result": {
        "path": (
            "history/internal_docs/"
            "goal5831_public_gpu_surface_terminology_and_denominator_result_20260830.json"
        ),
        "sha256": (
            "648335944aa3ad44a8cd265ce5a42ee08c27b21e2d320ae4f7ec6609f64124c1"
        ),
    },
    "goal5832_authority": {
        "path": (
            "history/internal_docs/"
            "goal5832_protocol_shape_algebra_authority_v1_20260830.json"
        ),
        "sha256": (
            "33db5c7c9c9403cc3c8f1f426fdf1ba594fd6c4a8d94608ab41e50dbe7be5200"
        ),
    },
    "goal5835_result": {
        "path": (
            "history/internal_docs/"
            "goal5835_sui_derived_edge_crossing_mapping_result_20260830.json"
        ),
        "sha256": (
            "ae370da1ca5ac96562d0956438e7c6c8eee39fddf2d9894953db8e956c47ccff"
        ),
    },
    "goal5836_a1_authority": {
        "path": (
            "history/internal_docs/goal5836_a1_source_fidelity_20260901/"
            "SOURCE_FIDELITY_AUTHORITY.json"
        ),
        "sha256": (
            "f05b026c2e96506466a400de71ee8ab6893f8deecb547447f29b8af567842c5f"
        ),
    },
    "goal5835_goal5836_strict_audit": {
        "path": (
            "history/internal_docs/goal5835_goal5836_strict_audit_20260901/"
            "STRICT_AUDIT_AUTHORITY.json"
        ),
        "sha256": (
            "bb58e1f0fc247f01f4636e985cef93b117c574e75b60f16e845f0e080f5820a5"
        ),
    },
    "successor_local_receipt": {
        "path": (
            "history/internal_docs/"
            "successor_owner_grouped_any_hit_local_validation_20260901.json"
        ),
        "sha256": (
            "6e9ed9334efb33a5164a18c4938a41688615816853b9785ef4e308e88d24bcf6"
        ),
    },
    "optix8_preflight": {
        "path": (
            "history/internal_docs/successor_owner_grouped_pod_20260902/"
            "owner_grouped_preflight_v2_optix8_7ec6b67.json"
        ),
        "sha256": (
            "9f87eab8d383b0fe56a70431bdef1bfc09dbeb03ff4da8bd493cb0c002185e32"
        ),
    },
    "optix8_native_build": {
        "path": (
            "history/internal_docs/successor_owner_grouped_pod_20260902/"
            "owner_grouped_native_build_optix8_7ec6b67.json"
        ),
        "sha256": (
            "679b0db35c64afc554d4095300a1431d99772ffb5bf211e7635572ba718e04cb"
        ),
    },
    "optix8_gpu_result": {
        "path": (
            "history/internal_docs/successor_owner_grouped_pod_20260902/"
            "owner_grouped_gpu_result_optix8_final_7ec6b67.json"
        ),
        "sha256": (
            "59e50a9f121f13b5b32fc13f2c9f6550a6756a3b48ad1a065fe824c60a93463f"
        ),
    },
    "optix9_failure_log": {
        "path": (
            "history/internal_docs/successor_owner_grouped_pod_20260902/"
            "owner_grouped_preflight_v2_optix9_7ec6b67.log"
        ),
        "sha256": (
            "a0887dc1de3f7ac7291463755821aa5d9eef5de8364a049f63d5fa3a60e43f4f"
        ),
    },
    "optix9_failure_exit_code": {
        "path": (
            "history/internal_docs/successor_owner_grouped_pod_20260902/"
            "owner_grouped_preflight_v2_optix9_7ec6b67.exit_code"
        ),
        "sha256": (
            "4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865"
        ),
    },
    "final_checksum_manifest": {
        "path": (
            "history/internal_docs/successor_owner_grouped_pod_20260902/"
            "owner_grouped_final_7ec6b67_SHA256SUMS"
        ),
        "sha256": (
            "b1efde198887b8d8ecce2873d6702026833f230382e9dd3232931a39118ec837"
        ),
    },
    "final_bundle": {
        "path": (
            "history/internal_docs/successor_owner_grouped_pod_20260902/"
            "owner_grouped_final_bundle_7ec6b67.tar.gz"
        ),
        "sha256": (
            "8946473aea9bb4598e830d3a78771407c6798618cd3f4ab789fc280cf62d4b9d"
        ),
    },
}

SOURCE_GROUPS = {
    "classification_basis": (
        "AGENTS.md",
        "scripts/goal5832_protocol_shape_algebra.py",
        "src/rtdsl/v4.py",
        "src/rtdsl/v4_callback_lifecycle.py",
        "src/rtdsl/__init__.py",
    ),
    "generic_behavior": (
        "src/rtdsl/v4_owner_grouped_any_hit.py",
    ),
    "curve_provider": (
        "src/rtdsl/v4_curve_owner_grouped_any_hit.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_standard_library.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_compiler.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_prepared_runtime.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_public.py",
        "src/rtdsl/v4_public_builtin_curve.py",
        "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
        "src/native/optix/rtdl_optix_api.cpp",
    ),
    "application": (
        "case_studies/linear_rtccd_owner_grouped/__init__.py",
        "case_studies/linear_rtccd_owner_grouped/fixtures.py",
        "case_studies/linear_rtccd_owner_grouped/independent_oracle.py",
        "case_studies/linear_rtccd_owner_grouped/linear_rtccd_owner_grouped.py",
        "case_studies/linear_rtccd_owner_grouped/run_local_validation.py",
        "case_studies/linear_rtccd_owner_grouped/README.md",
    ),
    "tooling_and_tests": (
        "scripts/build_v4_optix_native_snapshot.py",
        "scripts/successor_owner_grouped_pod_preflight.py",
        "scripts/successor_linear_rtccd_owner_grouped_pod_runner.py",
        "scripts/goal5837_freeze_owner_grouped_classification.py",
        "tests/successor_owner_grouped_any_hit_contract_test.py",
        "tests/successor_linear_rtccd_owner_grouped_app_test.py",
        "tests/successor_owner_grouped_gpu_tooling_test.py",
        "tests/goal5837_owner_grouped_classification_test.py",
    ),
}


class Goal5837Error(RuntimeError):
    """Fail-closed Goal5837 authority diagnostic."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise Goal5837Error(code)


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Goal5837Error(f"DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def load_json_exact(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="ascii", errors="strict"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=lambda token: (_ for _ in ()).throw(
            Goal5837Error(f"NONFINITE_JSON:{token}")
        ),
    )
    _require(isinstance(value, dict), "JSON_ROOT_NOT_OBJECT")
    return value


def _identity(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    _require(path.is_file(), f"MISSING_FILE:{relative}")
    data = path.read_bytes()
    return {"path": relative, "bytes": len(data), "sha256": _sha_bytes(data)}


def _historical_identities() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for label, expected in HISTORICAL_INPUTS.items():
        row = _identity(expected["path"])
        _require(
            row["sha256"] == expected["sha256"],
            f"HISTORICAL_IDENTITY_DRIFT:{label}",
        )
        rows[label] = row
    return rows


def _source_inventory() -> dict[str, list[dict[str, Any]]]:
    return {
        group: [_identity(relative) for relative in sorted(paths)]
        for group, paths in sorted(SOURCE_GROUPS.items())
    }


def _class_values(source: str, class_name: str) -> list[str]:
    tree = ast.parse(source)
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    ]
    _require(len(classes) == 1, f"CLASS_CARDINALITY:{class_name}")
    values = []
    for node in classes[0].body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        if not isinstance(node.targets[0], ast.Name):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            values.append(node.value.value)
    return values


def _literal_assignment(source: str, name: str) -> Any:
    matches = []
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        if isinstance(node.targets[0], ast.Name) and node.targets[0].id == name:
            value = node.value
            if isinstance(value, ast.Call) and len(value.args) == 1:
                value = value.args[0]
            matches.append(ast.literal_eval(value))
    _require(len(matches) == 1, f"ASSIGNMENT_CARDINALITY:{name}")
    return matches[0]


def _class_methods(source: str, class_name: str) -> set[str]:
    tree = ast.parse(source)
    classes = [node for node in ast.walk(tree)
               if isinstance(node, ast.ClassDef) and node.name == class_name]
    _require(len(classes) == 1, f"CLASS_CARDINALITY:{class_name}")
    return {
        node.name for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _function_type_names(source: str, function_name: str) -> list[str]:
    tree = ast.parse(source)
    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    ]
    _require(len(functions) == 1, f"FUNCTION_CARDINALITY:{function_name}")
    return sorted({
        node.id for node in ast.walk(functions[0])
        if isinstance(node, ast.Name) and node.id.endswith("Protocol")
    })


def _surface_observation() -> dict[str, Any]:
    lifecycle_source = (ROOT / "src/rtdsl/v4_callback_lifecycle.py").read_text(
        encoding="utf-8", errors="strict")
    stable_v4_source = (ROOT / "src/rtdsl/v4.py").read_text(
        encoding="utf-8", errors="strict")
    root_source = (ROOT / "src/rtdsl/__init__.py").read_text(
        encoding="utf-8", errors="strict")
    public_source = (
        ROOT / "src/rtdsl/v4_curve_owner_grouped_any_hit_public.py"
    ).read_text(encoding="utf-8", errors="strict")

    protocol_values = _class_values(lifecycle_source, "ProtocolFamily")
    _require(tuple(protocol_values) == STABLE_CONSTRUCTORS,
             "STABLE_PROTOCOL_ENUM_DRIFT")
    compile_protocol_types = _function_type_names(
        lifecycle_source, "compile_protocol_program")
    _require(
        compile_protocol_types
        == ["BoundedRelationProtocol", "TriangleReductionProtocol"],
        "STABLE_PROTOCOL_DISPATCH_DRIFT",
    )
    stable_all = set(_literal_assignment(stable_v4_source, "__all__"))
    root_lazy = _literal_assignment(root_source, "_LAZY_EXPORTS")
    root_all = _literal_assignment(root_source, "__all__")
    expected_lazy = {
        name: (".v4_curve_owner_grouped_any_hit_public", name)
        for name in SUCCESSOR_EXPORTS
    }
    for name, expected in expected_lazy.items():
        _require(root_lazy.get(name) == expected, f"ROOT_LAZY_EXPORT_DRIFT:{name}")
        _require(root_all.count(name) == 1, f"ROOT_ALL_EXPORT_DRIFT:{name}")
        _require(name not in stable_all, f"STABLE_V4_SUCCESSOR_EXPORT:{name}")

    lifecycle = {}
    for class_name, expected_methods in SUCCESSOR_LIFECYCLE.items():
        methods = _class_methods(public_source, class_name)
        _require(set(expected_methods) <= methods,
                 f"SUCCESSOR_LIFECYCLE_DRIFT:{class_name}")
        lifecycle[class_name] = list(expected_methods)

    generic_modules = (
        "src/rtdsl/v4_owner_grouped_any_hit.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_standard_library.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_compiler.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_prepared_runtime.py",
        "src/rtdsl/v4_curve_owner_grouped_any_hit_public.py",
    )
    for relative in generic_modules:
        source = (ROOT / relative).read_text(encoding="utf-8", errors="strict")
        for term in APPLICATION_TERMS:
            _require(
                re.search(rf"\b{re.escape(term)}\b", source, re.IGNORECASE) is None,
                f"APPLICATION_TERM_IN_ENGINE:{relative}:{term}",
            )

    behavior = (ROOT / "src/rtdsl/v4_owner_grouped_any_hit.py").read_text(
        encoding="utf-8", errors="strict")
    wrapper = (
        ROOT / "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py"
    ).read_text(encoding="utf-8", errors="strict")
    for marker in (
        'class OwnerGroupedReduction(str, Enum):',
        'BOOL_OR = "bool_or"',
        'device_operation": "atomic_or_u32"',
    ):
        _require(marker in behavior, f"GENERIC_BEHAVIOR_MARKER_MISSING:{marker}")
    for marker in ("optixTrace(", "atomicOr(params.owner_hit_bits + owner, 1u)",
                   "optixIgnoreIntersection();"):
        _require(marker in wrapper, f"WRAPPER_MARKER_MISSING:{marker}")

    app_source = (
        ROOT
        / "case_studies/linear_rtccd_owner_grouped/linear_rtccd_owner_grouped.py"
    ).read_text(encoding="utf-8", errors="strict")
    _require("collision" in app_source.lower(), "APP_SEMANTICS_NOT_APP_OWNED")

    return {
        "stable_v4_module": "rtdsl.v4",
        "stable_protocol_family_values": protocol_values,
        "compile_protocol_program_admitted_types": compile_protocol_types,
        "stable_v4_successor_export_count": 0,
        "root_successor_exports": list(SUCCESSOR_EXPORTS),
        "root_successor_export_count": len(SUCCESSOR_EXPORTS),
        "root_successor_export_occurrence_count_each": 1,
        "public_lifecycle": lifecycle,
        "closed_behavior": "OWNER_GROUPED_ANY_HIT/BOOL_OR",
        "first_physical_provider": "OPTIX_BUILTIN_ROUND_LINEAR_CURVE",
        "trusted_device_operation": "atomic_or_u32",
        "true_traversal_marker": "optixTrace",
        "continue_traversal_marker": "optixIgnoreIntersection",
        "generic_engine_application_vocabulary_matches": 0,
        "application_semantics_location": (
            "case_studies/linear_rtccd_owner_grouped"
        ),
    }


def _classification() -> dict[str, Any]:
    return {
        "exact_verdict": EXACT_CLASSIFICATION,
        "stable_v4_fixed_constructor_count_before_goal5837": 2,
        "stable_v4_fixed_constructor_count_after_goal5837": 2,
        "stable_v4_fixed_constructor_ids": list(STABLE_CONSTRUCTORS),
        "root_exported_closed_successor_route_count": 1,
        "root_exported_closed_successor_route_ids": [
            "builtin_curve_owner_grouped_any_hit_bool_or_v1"
        ],
        "goal5832_registered_successor_family_shape_count": 0,
        "prospective_frozen_core_new_shape_exam_count": 0,
        "heterogeneous_count_sum_forbidden": True,
        "forbidden_stable_constructor_total": 3,
        "reason": (
            "the successor has a closed root-exported lifecycle, but is absent "
            "from rtdsl.v4 ProtocolFamily, compile_protocol_program, and the "
            "Goal5832 family-shape/protocol-instance registry"
        ),
    }


def _claim_source_matrix() -> list[dict[str, Any]]:
    return [
        {
            "claim_id": "C01_GENERIC_BEHAVIOR_EXISTS",
            "authorized": True,
            "disposition": "SUPPORTED_INTERNAL_ARCHITECTURE_FACT",
            "statement": "OWNER_GROUPED_ANY_HIT/BOOL_OR is app-neutral generic behavior.",
            "source_ids": ["src.successor_behavior", "src.curve_provider"],
        },
        {
            "claim_id": "C02_ROOT_CLOSED_ROUTE_EXISTS",
            "authorized": True,
            "disposition": "SUPPORTED_INTERNAL_SURFACE_FACT",
            "statement": "One root-exported closed successor lifecycle exists.",
            "source_ids": ["src.root_public_surface", "src.curve_provider"],
        },
        {
            "claim_id": "C03_BOUNDED_APP_EXISTS",
            "authorized": True,
            "disposition": "SUPPORTED_INTERNAL_CASE_STUDY_FACT",
            "statement": "A bounded linear RT-CCD case study consumes the generic route.",
            "source_ids": ["src.linear_rtccd_app", "src.local_receipt"],
        },
        {
            "claim_id": "C04_OPTIX8_FUNCTIONAL_PARITY",
            "authorized": True,
            "disposition": "SUPPORTED_EXACT_PROFILE_FUNCTIONAL_FACT",
            "statement": "The exact OptiX 8 profile passed 30/30 true launches and oracle matches.",
            "source_ids": ["src.optix8_result", "src.optix8_native_build"],
        },
        {
            "claim_id": "C05_STABLE_CONSTRUCTOR_COUNT_TWO",
            "authorized": True,
            "disposition": "SUPPORTED_STABLE_SURFACE_FACT",
            "statement": "The stable rtdsl.v4 fixed-constructor count remains two.",
            "source_ids": ["src.goal5832_authority", "src.v4_stable_surface"],
        },
        {
            "claim_id": "C06_THIRD_STABLE_CONSTRUCTOR",
            "authorized": False,
            "disposition": "FORBIDDEN_RETROSPECTIVE_PROMOTION",
            "statement": "The successor is a third stable V4 fixed constructor.",
            "source_ids": ["src.v4_stable_surface", "src.root_public_surface"],
        },
        {
            "claim_id": "C07_REGISTERED_GOAL5832_SHAPE_INSTANCE",
            "authorized": False,
            "disposition": "NOT_IMPLEMENTED_OR_REGISTERED",
            "statement": "The successor is a Goal5832 family-shape/protocol-instance registration.",
            "source_ids": ["src.goal5832_authority", "src.v4_stable_surface"],
        },
        {
            "claim_id": "C08_PROSPECTIVE_GENERALIZATION",
            "authorized": False,
            "disposition": "FORBIDDEN_RETROSPECTIVE_RELABEL",
            "statement": "The already-built successor is a prospective frozen-core generalization success.",
            "source_ids": ["src.goal5832_authority", "src.internal_review_policy"],
        },
        {
            "claim_id": "C09_PERFORMANCE_OR_SPEEDUP",
            "authorized": False,
            "disposition": "DEFERRED_REQUIRES_PREREGISTERED_TIMING_STUDY",
            "statement": "The route has a performance or speedup result.",
            "source_ids": ["src.optix8_result", "src.internal_review_policy"],
        },
        {
            "claim_id": "C10_PAPER_APP_OR_FULL_REPRODUCTION",
            "authorized": False,
            "disposition": "FORBIDDEN_BY_EVIDENCE_SCOPE",
            "statement": "The bounded case study is a Paper App or full paper reproduction.",
            "source_ids": ["src.linear_rtccd_app", "src.goal5836_a1_authority"],
        },
        {
            "claim_id": "C11_EXTERNAL_CONSENSUS",
            "authorized": False,
            "disposition": "DEFERRED_BY_OWNER",
            "statement": "Goal5837 has external review or multi-AI consensus.",
            "source_ids": ["src.internal_review_policy"],
        },
        {
            "claim_id": "C12_OPTIX9_FUNCTIONAL_COVERAGE",
            "authorized": False,
            "disposition": "UNAVAILABLE_ON_R550_DRIVER",
            "statement": "The successor has OptiX 9 functional execution evidence.",
            "source_ids": ["src.optix9_failure", "src.optix8_result"],
        },
    ]


def _source_registry() -> dict[str, dict[str, Any]]:
    """Resolve every claim-source ID to files or authority fields."""

    return {
        "src.curve_provider": {
            "source_group": "curve_provider",
            "authority_fields": [
                "surface_observation.first_physical_provider",
                "surface_observation.trusted_device_operation",
            ],
        },
        "src.goal5832_authority": {
            "historical_input": "goal5832_authority",
            "authority_fields": ["classification"],
        },
        "src.goal5836_a1_authority": {
            "historical_input": "goal5836_a1_authority",
            "authority_fields": ["claim_boundary.paper_app_or_full_reproduction_claim"],
        },
        "src.internal_review_policy": {
            "paths": ["AGENTS.md"],
            "authority_fields": ["review_state", "claim_boundary"],
        },
        "src.linear_rtccd_app": {
            "source_group": "application",
            "authority_fields": ["surface_observation.application_semantics_location"],
        },
        "src.local_receipt": {
            "historical_input": "successor_local_receipt",
            "authority_fields": ["evidence_summary.local_reference"],
        },
        "src.optix8_native_build": {
            "historical_input": "optix8_native_build",
            "authority_fields": ["evidence_summary.optix8_native_build_status"],
        },
        "src.optix8_result": {
            "historical_input": "optix8_gpu_result",
            "authority_fields": ["evidence_summary.optix8_functional"],
        },
        "src.optix9_failure": {
            "historical_inputs": [
                "optix9_failure_log", "optix9_failure_exit_code"
            ],
            "authority_fields": ["evidence_summary.optix9_functional_status"],
        },
        "src.root_public_surface": {
            "paths": ["src/rtdsl/__init__.py"],
            "authority_fields": ["surface_observation.root_successor_exports"],
        },
        "src.successor_behavior": {
            "source_group": "generic_behavior",
            "authority_fields": ["surface_observation.closed_behavior"],
        },
        "src.v4_stable_surface": {
            "paths": [
                "src/rtdsl/v4.py", "src/rtdsl/v4_callback_lifecycle.py"
            ],
            "authority_fields": [
                "surface_observation.stable_protocol_family_values",
                "surface_observation.compile_protocol_program_admitted_types",
            ],
        },
    }


def _validate_local_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(receipt)
    seal = body.pop("receipt_sha256", None)
    _require(seal == _sha_bytes(_canonical(body)), "LOCAL_RECEIPT_SEAL_MISMATCH")
    expected = {
        "schema": "rtdl.successor_owner_grouped_any_hit.local_validation.v3",
        "status": "LOCAL_RECEIPT_PASS__GPU_FUNCTIONAL_EVIDENCE_IS_SEPARATE",
        "registered_semantic_case_count": 6,
        "registered_scale_case_count": 3,
        "registered_local_case_count": 9,
        "matching_local_case_count": 9,
        "optix_launch_count": 0,
        "gpu_correctness_evidence_count": 0,
        "performance_timing_count": 0,
        "external_review_count": 0,
        "benchmark_app_claimed": False,
        "full_paper_reproduction_claimed": False,
    }
    for key, value in expected.items():
        _require(receipt.get(key) == value, f"LOCAL_RECEIPT_FIELD:{key}")
    _require(receipt.get("frozen_goal5835_goal5836_files_modified") is False,
             "FROZEN_PREDECESSOR_MUTATION_REPORTED")
    return expected


def _validate_gpu_result(result: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema": "rtdl.successor_owner_grouped_any_hit.pod_validation.v2",
        "status": "PASS__TRUE_OPTIX_PARITY_AND_PREPARED_REUSE",
        "git_commit": GPU_EXECUTION_CHECKPOINT,
        "workload_count": 10,
        "registered_local_workload_count": 6,
        "scale_workload_count": 4,
        "repeat_count_per_workload": 3,
        "matching_gpu_execution_count": 30,
        "true_optix_launch_count": 30,
        "all_independent_oracles_match": True,
        "all_true_optix_receipts_valid": True,
        "all_prepared_reuse_counts_match": True,
        "registered_performance_timing_count": 0,
        "diagnostic_timing_sample_count": 30,
        "performance_claimed": False,
        "author_code_executed": False,
        "benchmark_app_claimed": False,
        "full_paper_reproduction_claimed": False,
        "external_review_count": 0,
    }
    for key, value in expected.items():
        _require(result.get(key) == value, f"GPU_RESULT_FIELD:{key}")
    _require(result.get("git_status_before_run") == [], "GPU_DIRTY_BEFORE")
    _require(result.get("git_status_after_run") == [], "GPU_DIRTY_AFTER")
    workloads = result.get("workloads")
    _require(isinstance(workloads, list) and len(workloads) == 10,
             "GPU_WORKLOAD_ROWS")
    _require(sum(len(row.get("executions", [])) for row in workloads) == 30,
             "GPU_EXECUTION_ROWS")
    for row in workloads:
        _require(len(row.get("executions", [])) == 3,
                 "GPU_REPEAT_CARDINALITY")
        for execution in row["executions"]:
            traversal = execution.get("traversal_receipt", {})
            _require(
                traversal.get("physical_executor_classification")
                == "optix_traversal_observed",
                "GPU_TRAVERSAL_CLASSIFICATION",
            )
            _require(
                traversal.get("expected_program_observed_at_receipt_edge") is True,
                "GPU_PROGRAM_NOT_OBSERVED",
            )
    largest = max(
        workloads, key=lambda row: row["independent_oracle_evaluated_pair_count"]
    )
    largest_summary = {
        "case_id": largest["case_id"],
        "owner_count": largest["owner_count"],
        "primitive_count": largest["primitive_count"],
        "query_count": largest["query_count"],
        "independent_oracle_evaluated_pair_count": (
            largest["independent_oracle_evaluated_pair_count"]
        ),
        "independent_oracle_intersecting_pair_count": (
            largest["independent_oracle_intersecting_pair_count"]
        ),
    }
    _require(largest_summary == {
        "case_id": "scale-o512-s8-h8-d1",
        "owner_count": 512,
        "primitive_count": 4096,
        "query_count": 1024,
        "independent_oracle_evaluated_pair_count": 4194304,
        "independent_oracle_intersecting_pair_count": 1024,
    }, "GPU_LARGEST_WORKLOAD_DRIFT")
    return {**expected, "largest_workload": largest_summary}


def _bundle_summary() -> dict[str, Any]:
    manifest_path = ROOT / HISTORICAL_INPUTS["final_checksum_manifest"]["path"]
    bundle_path = ROOT / HISTORICAL_INPUTS["final_bundle"]["path"]
    entries = []
    seen = set()
    for line in manifest_path.read_text(encoding="ascii", errors="strict").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/]+)", line)
        _require(match is not None, "CHECKSUM_MANIFEST_FORMAT")
        digest, name = match.groups()
        _require(name not in seen, "CHECKSUM_MANIFEST_DUPLICATE")
        seen.add(name)
        path = manifest_path.parent / name
        _require(path.is_file(), f"CHECKSUM_TARGET_MISSING:{name}")
        _require(_sha_bytes(path.read_bytes()) == digest,
                 f"CHECKSUM_TARGET_MISMATCH:{name}")
        entries.append({"path": name, "sha256": digest})
    _require(len(entries) == 6, "CHECKSUM_MANIFEST_CARDINALITY")

    with tarfile.open(bundle_path, "r:gz") as archive:
        members = archive.getmembers()
    names = []
    for member in members:
        pure = PurePosixPath(member.name)
        _require(not pure.is_absolute() and ".." not in pure.parts,
                 "UNSAFE_BUNDLE_MEMBER")
        _require(member.isfile() or member.isdir(), "UNSUPPORTED_BUNDLE_MEMBER")
        names.append(member.name.rstrip("/"))
    _require(len(names) == len(set(names)), "DUPLICATE_BUNDLE_MEMBER")
    for entry in entries:
        _require(entry["path"] in names,
                 f"CHECKSUM_TARGET_NOT_IN_BUNDLE:{entry['path']}")
    return {
        "checksum_entry_count": len(entries),
        "all_checksum_targets_match": True,
        "bundle_member_count": len(members),
        "bundle_paths_safe_and_unique": True,
        "checksum_entries": entries,
    }


def _evidence_summary() -> dict[str, Any]:
    local = load_json_exact(
        ROOT / HISTORICAL_INPUTS["successor_local_receipt"]["path"])
    gpu = load_json_exact(ROOT / HISTORICAL_INPUTS["optix8_gpu_result"]["path"])
    preflight = load_json_exact(ROOT / HISTORICAL_INPUTS["optix8_preflight"]["path"])
    native = load_json_exact(ROOT / HISTORICAL_INPUTS["optix8_native_build"]["path"])
    _require(
        preflight.get("status")
        == "PASS__COMPILER_AND_OPTIX_RUNTIME_ABI_READY_FOR_NATIVE_BUILD",
        "OPTIX8_PREFLIGHT_STATUS",
    )
    _require(preflight.get("git_commit") == GPU_EXECUTION_CHECKPOINT,
             "OPTIX8_PREFLIGHT_COMMIT")
    _require(preflight.get("optix_launch_count") == 0,
             "PREFLIGHT_LAUNCH_OVERCLAIM")
    _require(
        native.get("status")
        == "PASS__FRESH_NATIVE_BUILT_AND_REQUIRED_SYMBOLS_EXPORTED",
        "OPTIX8_NATIVE_STATUS",
    )
    _require(native.get("git_commit") == GPU_EXECUTION_CHECKPOINT,
             "OPTIX8_NATIVE_COMMIT")
    _require(native.get("all_required_symbols_exported") is True,
             "OPTIX8_NATIVE_SYMBOLS")
    return {
        "local_reference": _validate_local_receipt(local),
        "optix8_preflight_status": preflight["status"],
        "optix8_native_build_status": native["status"],
        "optix8_functional": _validate_gpu_result(gpu),
        "optix9_functional_status": "UNAVAILABLE__OPTIX_INIT_7801_ON_R550",
        "performance_result_count": 0,
        "paper_app_result_count": 0,
        "external_review_count": 0,
    }


def _historical_validator_context() -> dict[str, Any]:
    """Expose why the old repository-wide custody check is no longer clean."""

    result = load_json_exact(
        ROOT / HISTORICAL_INPUTS["goal5831_scope_result"]["path"])
    rows = [
        row for row in result.get("source_authorities", [])
        if row.get("path") == "src/rtdsl/__init__.py"
    ]
    _require(len(rows) == 1, "GOAL5831_ROOT_IDENTITY_CARDINALITY")
    historical = rows[0]
    current = _identity("src/rtdsl/__init__.py")
    _require(historical != current, "EXPECTED_POST_GOAL5831_ROOT_EVOLUTION_ABSENT")
    return {
        "status": (
            "PREEXISTING_HISTORICAL_CUSTODY_CHECK_NOT_COMPOSITIONAL_WITH_"
            "LATER_ROOT_EXPORTS"
        ),
        "goal5831_frozen_root_identity": historical,
        "current_root_identity": current,
        "identities_differ": True,
        "goal5832_full_current_repository_validation_claimed": False,
        "goal5832_usage_in_goal5837": (
            "hash_bound terminology and count baseline only; current stable "
            "and root surfaces are independently derived from AST"
        ),
        "historical_manifest_rewritten": False,
    }


def _review_state() -> dict[str, Any]:
    return {
        "review_type": "INTERNAL_HOSTILE_SELF_REVIEW_ONLY",
        "external_review_requested": False,
        "external_review_count": 0,
        "external_review_status": "DEFERRED_BY_OWNER_DURING_TRAVEL",
        "consensus_claimed": False,
        "pod_used_by_goal5837": False,
        "new_gpu_execution_count": 0,
    }


def _seal(document: dict[str, Any]) -> str:
    body = copy.deepcopy(document)
    body["authority_sha256"] = ""
    return _sha_bytes(DOMAIN + _canonical(body))


def build_authority() -> dict[str, Any]:
    historical = _historical_identities()
    goal5832 = load_json_exact(ROOT / HISTORICAL_INPUTS["goal5832_authority"]["path"])
    _require(goal5832.get("current_counts", {}).get("fixed_protocol_constructors") == 2,
             "GOAL5832_FIXED_CONSTRUCTOR_COUNT")
    _require(
        goal5832.get("current_counts", {}).get(
            "prospective_frozen_core_new_shape_exams") == 0,
        "GOAL5832_PROSPECTIVE_COUNT",
    )
    document = {
        "schema": "rtdl.goal5837.owner_grouped_classification.v1",
        "date": "2026-09-02",
        "goal": "Goal5837",
        "status": "COMPLETE__CLASSIFICATION_FROZEN__NO_CLAIM_UPGRADE",
        "scope": (
            "freeze and classify the owner-grouped successor route and its "
            "bounded linear RT-CCD functional evidence"
        ),
        "input_checkpoint": INPUT_CHECKPOINT,
        "gpu_execution_checkpoint": GPU_EXECUTION_CHECKPOINT,
        "classification": _classification(),
        "surface_observation": _surface_observation(),
        "historical_inputs": historical,
        "source_inventory": _source_inventory(),
        "evidence_summary": _evidence_summary(),
        "historical_validator_context": _historical_validator_context(),
        "bundle_verification": _bundle_summary(),
        "source_registry": _source_registry(),
        "claim_source_matrix": _claim_source_matrix(),
        "review_state": _review_state(),
        "claim_boundary": {
            "additional_root_exported_closed_route": True,
            "third_stable_v4_fixed_constructor": False,
            "goal5832_registered_protocol_shape_instance": False,
            "prospective_generalization_success": False,
            "performance_or_speedup_claim": False,
            "paper_app_or_full_reproduction_claim": False,
            "external_consensus_claim": False,
            "optix9_functional_claim": False,
        },
        "next_separate_gates": [
            "Goal5838 preregistered new-topology prospective exam",
            "external review after the owner returns from travel",
            "preregistered Embree/timing study before performance wording",
            "explicit stable-V4 admission transaction if later desired",
        ],
        "authority_sha256": "",
    }
    document["authority_sha256"] = _seal(document)
    validate_policy(document)
    return document


def validate_policy(document: dict[str, Any]) -> None:
    _require(document.get("schema") == "rtdl.goal5837.owner_grouped_classification.v1",
             "AUTHORITY_SCHEMA")
    _require(document.get("status")
             == "COMPLETE__CLASSIFICATION_FROZEN__NO_CLAIM_UPGRADE",
             "AUTHORITY_STATUS")
    _require(document.get("input_checkpoint") == INPUT_CHECKPOINT,
             "INPUT_CHECKPOINT_MISMATCH")
    _require(document.get("gpu_execution_checkpoint") == GPU_EXECUTION_CHECKPOINT,
             "GPU_CHECKPOINT_MISMATCH")
    _require(document.get("classification") == _classification(),
             "CLASSIFICATION_POLICY_MISMATCH")
    _require(document.get("claim_source_matrix") == _claim_source_matrix(),
             "CLAIM_SOURCE_MATRIX_MISMATCH")
    _require(document.get("source_registry") == _source_registry(),
             "SOURCE_REGISTRY_MISMATCH")
    _require(document.get("review_state") == _review_state(),
             "REVIEW_STATE_MISMATCH")
    expected_boundary = {
        "additional_root_exported_closed_route": True,
        "third_stable_v4_fixed_constructor": False,
        "goal5832_registered_protocol_shape_instance": False,
        "prospective_generalization_success": False,
        "performance_or_speedup_claim": False,
        "paper_app_or_full_reproduction_claim": False,
        "external_consensus_claim": False,
        "optix9_functional_claim": False,
    }
    _require(document.get("claim_boundary") == expected_boundary,
             "CLAIM_BOUNDARY_MISMATCH")
    matrix = document["claim_source_matrix"]
    ids = [row["claim_id"] for row in matrix]
    _require(len(ids) == len(set(ids)) == 12, "CLAIM_ID_DENOMINATOR")
    known_sources = set(document["source_registry"])
    _require(all(set(row["source_ids"]) <= known_sources for row in matrix),
             "UNKNOWN_CLAIM_SOURCE")
    inventory_paths = {
        item["path"]
        for rows in document.get("source_inventory", {}).values()
        for item in rows
    }
    for source_id, source in document["source_registry"].items():
        if "source_group" in source:
            _require(
                source["source_group"] in document.get("source_inventory", {}),
                f"SOURCE_GROUP_UNRESOLVED:{source_id}",
            )
        historical_labels = []
        if "historical_input" in source:
            historical_labels.append(source["historical_input"])
        historical_labels.extend(source.get("historical_inputs", []))
        _require(
            all(label in document.get("historical_inputs", {})
                for label in historical_labels),
            f"HISTORICAL_SOURCE_UNRESOLVED:{source_id}",
        )
        _require(
            all(path in inventory_paths for path in source.get("paths", [])),
            f"PATH_SOURCE_UNRESOLVED:{source_id}",
        )
        for dotted in source.get("authority_fields", []):
            value: Any = document
            for part in dotted.split("."):
                _require(
                    isinstance(value, dict) and part in value,
                    f"AUTHORITY_FIELD_UNRESOLVED:{source_id}:{dotted}",
                )
                value = value[part]
    evidence = document.get("evidence_summary", {})
    _require(evidence.get("performance_result_count") == 0,
             "PERFORMANCE_RESULT_PROMOTION")
    _require(evidence.get("paper_app_result_count") == 0,
             "PAPER_APP_PROMOTION")
    _require(evidence.get("external_review_count") == 0,
             "EXTERNAL_REVIEW_PROMOTION")
    historical_context = document.get("historical_validator_context", {})
    _require(
        historical_context.get("status")
        == "PREEXISTING_HISTORICAL_CUSTODY_CHECK_NOT_COMPOSITIONAL_WITH_LATER_ROOT_EXPORTS",
        "HISTORICAL_VALIDATOR_CONTEXT_MISSING",
    )
    _require(historical_context.get("identities_differ") is True,
             "HISTORICAL_ROOT_DRIFT_HIDDEN")
    _require(
        historical_context.get("goal5832_full_current_repository_validation_claimed")
        is False,
        "GOAL5832_CURRENT_REPOSITORY_OVERCLAIM",
    )
    _require(historical_context.get("historical_manifest_rewritten") is False,
             "HISTORICAL_MANIFEST_REWRITE")


def validate_authority(document: dict[str, Any]) -> None:
    _require(document.get("authority_sha256") == _seal(document),
             "AUTHORITY_SEAL_MISMATCH")
    validate_policy(document)
    expected = build_authority()
    _require(document == expected, "AUTHORITY_CURRENT_INPUT_MISMATCH")


def write_authority(path: Path = STORED_AUTHORITY) -> dict[str, Any]:
    document = build_authority()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(_pretty(document))
    temporary.replace(path)
    return document


def verify_stored(path: Path = STORED_AUTHORITY) -> dict[str, Any]:
    document = load_json_exact(path)
    validate_authority(document)
    return document


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.output is not None and args.verify_stored:
        raise SystemExit("choose --output or --verify-stored")
    if args.verify_stored:
        document = verify_stored()
    else:
        document = write_authority(args.output or STORED_AUTHORITY)
    print(json.dumps({
        "status": document["status"],
        "classification": document["classification"]["exact_verdict"],
        "stable_v4_fixed_constructor_count": document["classification"][
            "stable_v4_fixed_constructor_count_after_goal5837"],
        "root_exported_closed_successor_route_count": document["classification"][
            "root_exported_closed_successor_route_count"],
        "authority_sha256": document["authority_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
