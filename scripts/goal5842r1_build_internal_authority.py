#!/usr/bin/env python3
"""Build or verify Goal5842R1's bounded internal authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "history/internal_docs/goal5842r1_public_reuse_scalar_fastpath_20260903"
)
AUTHORITY_PATH = EVIDENCE / "GOAL5842R1_INTERNAL_AUTHORITY.json"
REPORT_PATH = EVIDENCE / "FINAL_TECHNICAL_REPORT.md"
REVIEW_PATH = EVIDENCE / "FINAL_INTERNAL_HOSTILE_SELF_REVIEW.md"
FORMAL_V12_AUTHORITY = (
    ROOT
    / "history/internal_docs/goal5842_causal_admission_cost_20260903"
    / "GOAL5842_FINAL_INTERNAL_AUTHORITY.json"
)
IMPLEMENTATION_COMMIT = "207e7afc4afd44ddef537f74d97c47ae323743b2"
AUTHORITY_DOMAIN = b"rtdl.goal5842r1.internal_authority.v1\0"

ARTIFACTS = {
    "PREMEASUREMENT_PLAN.md": (
        "33b4e43a3bbc2f65b2995005f6db43df18b1e32ff9ec00f73021d0c9cc5e3e1a"
    ),
    "POD_DIAGNOSTIC_V1.json": (
        "29754b15be9cbd79298f78ee1ccafd5c4fedc3d66c2769bdd62a30a77b681eb2"
    ),
    "POD_DIAGNOSTIC_V2_PREOUTPUT_FAILURE.md": (
        "a1a28fc7d28a7f1c3d8f1b79be3356f3e0a4582fb7510c390cfd0153811cb0b2"
    ),
    "POD_DIAGNOSTIC_V3_V4_PREOUTPUT_FAILURES.md": (
        "9db32e3823137fec23838f83857e9e8e63be54551e3399ec34810381cdfb0038"
    ),
    "POD_DIAGNOSTIC_V5.json": (
        "0dba648b742d5fceedcf1e102b27dad1ca729925dac90616f86926425727e40f"
    ),
    "LAYER_DIAGNOSTIC_V6.json": (
        "8b02be8273ef69d46815740452eeba0b9af9fed838e5e56577ca5c68c44754cc"
    ),
    "LAYER_DIAGNOSTIC_V7.json": (
        "ec165a8885ca057e8fe10c0338e7732c10d42a416ca9db1e3b09e8a91936a759"
    ),
    "POD_DIAGNOSTIC_V8.json": (
        "742c467507028aaf54f1f99451f825068cbc44ff1e1fc4607edd0a6437ee314e"
    ),
    "POD_DIAGNOSTIC_V9.json": (
        "4559a19a91d9c71da57f5055e440c74dddc172b8c1b4904491542e57dec86029"
    ),
    "POD_DIAGNOSTIC_V10.json": (
        "94044f5d37874c0cf9b6ac9a19ef5cb998a7be9814ed7fd39bd978d74197f4ec"
    ),
}

RESULT_SOURCES = {
    "POD_DIAGNOSTIC_V1.json": (
        "888b953d4ce50d3602db822e904aa600e3c971eb"
    ),
    "POD_DIAGNOSTIC_V5.json": (
        "66be2dcc9edbfb17d8e3e695b558399652d4c7c8"
    ),
    "LAYER_DIAGNOSTIC_V6.json": (
        "f518fa22ac208bac4904f76ffe2f0b387a7e0032"
    ),
    "LAYER_DIAGNOSTIC_V7.json": IMPLEMENTATION_COMMIT,
    "POD_DIAGNOSTIC_V8.json": IMPLEMENTATION_COMMIT,
    "POD_DIAGNOSTIC_V9.json": IMPLEMENTATION_COMMIT,
    "POD_DIAGNOSTIC_V10.json": IMPLEMENTATION_COMMIT,
}

IMPLEMENTATION_FILES = (
    "experiments/goal5798_premeasurement/rtdl_worker.py",
    "scripts/goal5798_profile_public_triangle.py",
    "scripts/goal5798_validate_immutable_input_reuse.py",
    "scripts/goal5842_gpu_identity_witness.py",
    "scripts/goal5842r1_profile_triangle_execute_layers.py",
    "scripts/goal5842r1_public_reuse_scalar_pod_runner.py",
    "src/rtdsl/v4.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_callback_lifecycle.py",
    "src/rtdsl/v4_callback_numba_codegen.py",
    "src/rtdsl/v4_triangle_reduction_optix_compiler.py",
    "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
    "src/rtdsl/v4_triangle_standard_library.py",
    "tests/goal5775_v4_formal_leaf_cache_test.py",
    "tests/goal5795_v4_public_lifecycle_test.py",
    "tests/goal5842_causal_admission_cost_test.py",
    "tests/goal5842_prepared_cache_commit_test.py",
)

FROZEN_CORE = {
    "src/rtdsl/v4_family_schema.py": (
        "2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224"
    ),
    "src/rtdsl/v4_generic_family_lifecycle.py": (
        "7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c"
    ),
    "src/rtdsl/v4_family.py": (
        "d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8"
    ),
}

EXPECTED_GPU = {
    "name": "NVIDIA RTX A6000",
    "uuid": "GPU-6457d4af-a4bb-bff5-a9d2-02f251ceca27",
    "compute_capability": "8.6",
    "driver_version": "550.127.08",
    "memory_total_mib": "49140",
}
EXPECTED_WORKLOAD = {
    "task": "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
    "input_sha256": (
        "d994f80418995342d0faa4bda84b42c2ef3604b2798de413a2813dd28dc039a7"
    ),
    "query_count": 16384,
    "triangle_count": 16384,
    "expected_scalar": 65530,
    "expected_per_ray_sha256": (
        "1c122906ae8e13897ce3f39274f405123f128fce69e4fefd9559b794a36c8fd3"
    ),
}


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _result_digest(value: Mapping[str, object]) -> str:
    body = dict(value)
    body.pop("result_sha256", None)
    return _sha256_bytes(_canonical_bytes(body))


def _authority_seal(value: Mapping[str, object]) -> str:
    body = dict(value)
    body["authority_sha256"] = ""
    return _sha256_bytes(AUTHORITY_DOMAIN + _canonical_bytes(body))


def _git_blob(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def _verify_implementation_files() -> list[dict[str, object]]:
    rows = []
    for name in IMPLEMENTATION_FILES:
        current = (ROOT / name).read_bytes()
        committed = _git_blob(IMPLEMENTATION_COMMIT, name)
        _require(current == committed, f"implementation drift from evidence commit: {name}")
        rows.append(
            {
                "path": name,
                "sha256": _sha256_bytes(current),
                "size_bytes": len(current),
            }
        )
    return rows


def _verify_frozen_boundaries() -> dict[str, object]:
    core_rows = []
    for name, expected in FROZEN_CORE.items():
        observed = _sha256_file(ROOT / name)
        _require(observed == expected, f"Goal5838 frozen-core drift: {name}")
        core_rows.append({"path": name, "sha256": observed})
    _require(
        _sha256_file(FORMAL_V12_AUTHORITY)
        == "79d5c50d3a78443c22f5e9c490438f26cad64e3b0127f6862b4d29bd747860b0",
        "formal Goal5842 V12 authority bytes changed",
    )
    formal = _load(FORMAL_V12_AUTHORITY)
    _require(
        formal.get("authority_sha256")
        == "5c8044d9204df6b5d622142aecab8fcd25990e2ca1a19c7c5055ef4e16a31e43"
        and formal.get("source_commit")
        == "04305fc820290cc183a599376f13d2fb48175233"
        and formal.get("claim_boundary", {}).get("optimization_result_included")
        is False,
        "formal Goal5842 V12 boundary changed",
    )
    return {
        "goal5838_frozen_core": core_rows,
        "goal5842_v12": {
            "path": str(FORMAL_V12_AUTHORITY.relative_to(ROOT)),
            "file_sha256": _sha256_file(FORMAL_V12_AUTHORITY),
            "authority_sha256": formal["authority_sha256"],
            "source_commit": formal["source_commit"],
            "optimization_result_included": False,
        },
    }


def _verify_result(name: str) -> dict[str, object]:
    value = _load(EVIDENCE / name)
    _require(
        value.get("status") == "PASS__NONFORMAL_ENGINEERING_DIAGNOSTIC",
        f"unexpected diagnostic status: {name}",
    )
    _require(value.get("source_commit") == RESULT_SOURCES[name], f"source drift: {name}")
    _require(value.get("result_sha256") == _result_digest(value), f"result seal drift: {name}")
    boundary = value.get("claim_boundary")
    _require(isinstance(boundary, dict), f"claim boundary absent: {name}")
    _require(boundary.get("formal_performance_evidence") is False, f"formal overclaim: {name}")
    public_key = (
        "public_or_manuscript_claim_authorized"
        if name.startswith("LAYER_")
        else "paper_or_public_speedup_authorized"
    )
    _require(boundary.get(public_key) is False, f"public overclaim: {name}")
    return value


def _verify_complete_run(name: str) -> dict[str, object]:
    value = _verify_result(name)
    _require(value.get("hardware") == EXPECTED_GPU, f"GPU identity drift: {name}")
    _require(value.get("workload") == EXPECTED_WORKLOAD, f"workload drift: {name}")
    correctness = value.get("correctness")
    _require(
        isinstance(correctness, dict)
        and correctness
        == {
            "diagnostic_per_ray_matches_exact_oracle": True,
            "diagnostic_scalar_matches_exact_oracle": True,
            "same_program_and_input_contract": True,
            "scalar_matches_exact_oracle": True,
        },
        f"correctness drift: {name}",
    )
    execute = value.get("execute")
    _require(isinstance(execute, dict), f"execute row absent: {name}")
    scalar = execute.get("scalar_boundary")
    _require(isinstance(scalar, dict), f"scalar boundary absent: {name}")
    receipt = scalar.get("fast_operation_receipt")
    _require(isinstance(receipt, dict), f"fast receipt absent: {name}")
    expected_boundary = {
        "execution_path": "device_resident_checked_u64_scalar_v7",
        "prepared_query_input_reused": True,
        "per_ray_u64_materialized_on_host": False,
        "event_rows_materialized_on_host": False,
        "public_output_scalar_bytes": 8,
    }
    _require(
        all(scalar.get(key) == expected for key, expected in expected_boundary.items()),
        f"scalar execution boundary drift: {name}",
    )
    expected_receipt = {
        "optix_launch_count": 1,
        "dynamic_accel_build_count": 0,
        "dynamic_device_upload_call_count": 0,
        "dynamic_device_upload_bytes": 0,
        "control_d2h_bytes": 12,
        "output_d2h_bytes": 8,
        "status_before_output": True,
        "role_counters_materialized": False,
        "prepared_input_reused": True,
        "total_auxiliary_cuda_kernel_launch_count": 0,
    }
    _require(
        all(receipt.get(key) == expected for key, expected in expected_receipt.items()),
        f"fast receipt drift: {name}",
    )
    _require(
        execute.get("scalar_steady", {}).get("sample_count") == 64
        and execute.get("diagnostic_steady", {}).get("sample_count") == 64,
        f"steady sample count drift: {name}",
    )
    additional = value.get("additional_gpu_validation")
    _require(isinstance(additional, dict), f"cross-family validation absent: {name}")
    relation = additional.get("bounded_relation")
    all_hit = additional.get("triangle_all_hit_count")
    _require(
        isinstance(relation, dict)
        and relation.get("exact_oracle_match") is True,
        f"relation oracle drift: {name}",
    )
    _require(
        isinstance(all_hit, dict)
        and all_hit.get("exact_oracle_match") is True
        and all_hit.get("expected_scalar") == 16384,
        f"all-hit oracle drift: {name}",
    )
    return value


def build_authority() -> dict[str, object]:
    for name, expected in ARTIFACTS.items():
        _require(_sha256_file(EVIDENCE / name) == expected, f"artifact drift: {name}")

    v1 = _verify_result("POD_DIAGNOSTIC_V1.json")
    v5 = _verify_result("POD_DIAGNOSTIC_V5.json")
    v6 = _verify_result("LAYER_DIAGNOSTIC_V6.json")
    v7 = _verify_result("LAYER_DIAGNOSTIC_V7.json")
    complete = [
        _verify_complete_run(name)
        for name in (
            "POD_DIAGNOSTIC_V8.json",
            "POD_DIAGNOSTIC_V9.json",
            "POD_DIAGNOSTIC_V10.json",
        )
    ]
    _require(REPORT_PATH.is_file() and REVIEW_PATH.is_file(), "final reports missing")
    implementation_rows = _verify_implementation_files()
    frozen = _verify_frozen_boundaries()

    artifact_rows = []
    for name, expected in ARTIFACTS.items():
        row: dict[str, object] = {
            "path": str((EVIDENCE / name).relative_to(ROOT)),
            "file_sha256": expected,
        }
        if name in RESULT_SOURCES:
            value = _load(EVIDENCE / name)
            row["source_commit"] = value["source_commit"]
            row["result_sha256"] = value["result_sha256"]
        artifact_rows.append(row)

    scalar_medians = [run["execute"]["scalar_steady"]["median_ms"] for run in complete]
    diagnostic_medians = [
        run["execute"]["diagnostic_steady"]["median_ms"] for run in complete
    ]
    relation_medians = [
        run["additional_gpu_validation"]["bounded_relation"]["reused_execute_ms"]
        for run in complete
    ]
    all_hit_medians = [
        run["additional_gpu_validation"]["triangle_all_hit_count"]["reused_execute_ms"]
        for run in complete
    ]
    result: dict[str, object] = {
        "schema": "rtdl.goal5842r1.internal_authority.v1",
        "status": (
            "PASS__GOAL5842R1_INTERNAL_IMPLEMENTATION_REPAIR_COMPLETE__"
            "FRESH_FAIR_BASELINE_AND_EXTERNAL_REVIEW_PENDING"
        ),
        "implementation_source_commit": IMPLEMENTATION_COMMIT,
        "implementation_files": implementation_rows,
        "frozen_boundaries": frozen,
        "evidence_artifacts": artifact_rows,
        "reports": [
            {
                "path": str(REPORT_PATH.relative_to(ROOT)),
                "sha256": _sha256_file(REPORT_PATH),
            },
            {
                "path": str(REVIEW_PATH.relative_to(ROOT)),
                "sha256": _sha256_file(REVIEW_PATH),
            },
        ],
        "hardware": EXPECTED_GPU,
        "workload": EXPECTED_WORKLOAD,
        "completion": {
            "accepted_complete_repeat_count": len(complete),
            "accepted_complete_repeat_names": ["V8", "V9", "V10"],
            "all_complete_repeats_exact_oracle": True,
            "all_complete_repeats_one_true_optix_launch": True,
            "all_complete_repeats_zero_reused_input_upload_bytes": True,
            "all_complete_repeats_scalar_only_public_output": True,
            "formal_leaf_cache_public_policy_implemented": True,
            "exact_immutable_prepared_input_reuse_implemented": True,
            "device_resident_checked_u64_scalar_lowering_implemented": True,
            "failed_attempt_records_retained": True,
            "internal_hostile_review_complete": True,
            "completion_depends_on_performance_threshold": False,
        },
        "descriptive_results": {
            "pre_scan_fix_scalar_steady_median_ms": {
                "V1": v1["execute"]["scalar_steady"]["median_ms"],
                "V5": v5["execute"]["scalar_steady"]["median_ms"],
            },
            "post_scan_fix_scalar_steady_median_ms": dict(
                zip(("V8", "V9", "V10"), scalar_medians, strict=True)
            ),
            "post_scan_fix_diagnostic_steady_median_ms": dict(
                zip(("V8", "V9", "V10"), diagnostic_medians, strict=True)
            ),
            "post_scan_fix_scalar_median_min_ms": min(scalar_medians),
            "post_scan_fix_scalar_median_max_ms": max(scalar_medians),
            "layer_public_api_median_ms": {
                "V6_before_scan_fix": v6["layers"]["public_api"]["median_ms"],
                "V7_after_scan_fix": v7["layers"]["public_api"]["median_ms"],
            },
            "layer_native_v7_median_ms": {
                "V6_before_scan_fix": v6["layers"]["native_v7_reused_input"]["median_ms"],
                "V7_after_scan_fix": v7["layers"]["native_v7_reused_input"]["median_ms"],
            },
            "bounded_relation_reused_execute_ms": dict(
                zip(("V8", "V9", "V10"), relation_medians, strict=True)
            ),
            "triangle_all_hit_reused_execute_ms": dict(
                zip(("V8", "V9", "V10"), all_hit_medians, strict=True)
            ),
        },
        "claim_boundary": {
            "goal5842r1_internal_implementation_repair_complete": True,
            "goal5842_v12_modified": False,
            "fresh_fair_direct_pyoptix_rtdl_baseline_complete": False,
            "second_hardware_generation_r1_replication_complete": False,
            "external_review_or_consensus": False,
            "public_performance_claim_authorized": False,
            "manuscript_performance_wording_authorized": False,
            "human_authoring_evidence_complete": False,
            "hardware_independent_timing_claimed": False,
            "arbitrary_application_performance_claimed": False,
            "private_audit_bypass_supported": False,
        },
        "authority_sha256": "",
    }
    result["authority_sha256"] = _authority_seal(result)
    return result


def verify_stored() -> dict[str, object]:
    observed = _load(AUTHORITY_PATH)
    _require(
        observed.get("authority_sha256") == _authority_seal(observed),
        "stored Goal5842R1 authority seal mismatch",
    )
    rebuilt = build_authority()
    _require(observed == rebuilt, "stored Goal5842R1 authority differs from rebuild")
    return observed


def write_output(path: Path) -> dict[str, object]:
    result = build_authority()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="ascii") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        stream.write("\n")
    return result


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args(argv)
    result = verify_stored() if args.verify_stored else write_output(args.output.resolve())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
