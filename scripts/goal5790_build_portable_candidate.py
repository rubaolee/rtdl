#!/usr/bin/env python3
"""Build the deterministic Goal5790 Home-functional/pre-POD source candidate.

The exact approved Goal5785 source is the immutable base.  This builder overlays
only the Goal5789/5790 semantic contract, reducer/runtime integration, paper-app
front door, tests and harness.  It ships no private cache and no target native;
the clean validator must build and preserve the target-local provider itself.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE_SOURCE = (
    ROOT / "history/internal_docs/goal5785_final_nine_app_source_v6_20260815.tar.gz"
)
EXPECTED_BASE_SOURCE_SHA256 = (
    "d1461498742e03a001662975b4ebb4dadb145d2a3027675c24f576c1b97c02d6"
)
OLD_SOURCE_MANIFEST = "history/internal_docs/goal5776_source_file_manifest.json"
SHARED_FREEZE = (
    "history/internal_docs/goal5789_contract_evidence_20260816/"
    "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json"
)
EXPECTED_VALUE_AND_FALLBACK = (
    "history/internal_docs/"
    "goal5790_preregistered_expected_value_and_fallback_20260816.json"
)
HOME_MACHINE_AUTHORITY = (
    "history/internal_docs/"
    "goal5790_frozen_home_machine_authority_20260816.json"
)
FIXED_OVERLAYS = (
    "src/rtdsl/v4_operation_evidence.py",
    "src/rtdsl/v4_fusion_ablation.py",
    "src/rtdsl/v4_checked_u64_device_reduction.py",
    "src/rtdsl/v4_triangle_reduction_device_runtime.py",
    "src/rtdsl/physical_execution_provenance.py",
    "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
    "tests/goal5778_v4_checked_u64_device_reduction_test.py",
    "docs/v4/semantic_physical_contract_calculus.md",
    "scripts/goal5789_independent_compatibility_checker.py",
    SHARED_FREEZE,
)
PROVENANCE_FILES = (
    "history/internal_docs/goal5789_semantic_physical_contract_calculus_result_20260816.json",
    "history/internal_docs/goal5789_semantic_physical_contract_calculus_technical_report_20260816.md",
    "history/internal_docs/self_review_goal5789_semantic_physical_contract_calculus_20260816.md",
    "history/internal_docs/call_for_review_goal5789_semantic_physical_contract_calculus_20260816.md",
    "history/internal_docs/goal5789_delivery_manifest_20260816.json",
    "history/internal_docs/goal5789_rule_to_source_map_20260816.md",
    "history/internal_docs/goal5789_primary_source_related_work_matrix_20260816.md",
    "history/internal_docs/goal5789_primary_source_bibliography_20260816.json",
    "history/internal_docs/goal5789_novelty_boundary_and_claim_kill_gates_20260816.md",
    "history/internal_docs/goal5790_t0_feasibility_adjudication_result_20260816.json",
    "history/internal_docs/goal5790_t0_feasibility_adjudication_report_20260816.md",
    "history/internal_docs/self_review_goal5790_t0_feasibility_adjudication_20260816.md",
    "history/internal_docs/goal5790_t0_delivery_manifest_20260816.json",
    "history/internal_docs/goal5790_same_source_same_cohort_fusion_ablation_plan_20260816.md",
    "history/internal_docs/goal5790_v2_home_s1_zero_worker_failure_result_20260816.json",
    "history/internal_docs/goal5790_v2_home_s1_zero_worker_failure_report_20260816.md",
    "history/internal_docs/goal5790_v3_home_s2_zero_worker_failure_result_20260816.json",
    "history/internal_docs/goal5790_v3_home_s2_zero_worker_failure_report_20260816.md",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_result_20260816.json",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_report_20260816.md",
    "history/internal_docs/diagnostic_goal5790_home_ptx_target_identity_20260816.py",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_20260816/PORTABLE_MANIFEST.json",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_20260816/logs/build.log",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_20260816/logs/cuda_host_compiler.log",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_20260816/logs/focused_tests.log",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_20260816/logs/gpu.log",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_20260816/logs/inspect_target.log",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_20260816/logs/nvcc.log",
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_20260816/logs/versions.log",
    "history/internal_docs/goal5790_v5_prefreeze_rejection_result_20260816.json",
    "history/internal_docs/goal5790_v5_prefreeze_rejection_report_20260816.md",
    "history/internal_docs/goal5790_v6_prefreeze_rejection_result_20260816.json",
    "history/internal_docs/goal5790_v6_prefreeze_rejection_report_20260816.md",
    "history/internal_docs/goal5790_v7_prefreeze_rejection_result_20260816.json",
    "history/internal_docs/goal5790_v7_prefreeze_rejection_report_20260816.md",
    EXPECTED_VALUE_AND_FALLBACK,
    HOME_MACHINE_AUTHORITY,
)
EXPECTED_PROVENANCE_SHA256 = {
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_result_20260816.json": (
        "6428ba811905081561ac01d3ebd0a390b57fad37880f49d63acff0e0eda1ce1c"),
    "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_report_20260816.md": (
        "163565c96ea37abc86f7b43bc8de25b46748982d98485bc62b891e22ff106dc9"),
    "history/internal_docs/goal5790_v5_prefreeze_rejection_result_20260816.json": (
        "5bf0a288af9ae27a06b83b03cc2b115de5a2a3b5b26e618843ab86369fa567bc"),
    "history/internal_docs/goal5790_v5_prefreeze_rejection_report_20260816.md": (
        "b60f5f807a60075ce467e949b0d45d1a1173d1109974ab8396a5feae45671bc4"),
    "history/internal_docs/goal5790_v6_prefreeze_rejection_result_20260816.json": (
        "c934e12de5585b14ed382da9d2416b1ab452bdf2450a2d686d778737b364312f"),
    "history/internal_docs/goal5790_v6_prefreeze_rejection_report_20260816.md": (
        "7ce28260985ba3ddcc500c25837d30186f9de929e9e53007b3bd4d0fb4eff248"),
    "history/internal_docs/goal5790_v7_prefreeze_rejection_result_20260816.json": (
        "4c19439962519e9884381701d7580874528f7d9986fcd5fbfdc78d8204aa6504"),
    "history/internal_docs/goal5790_v7_prefreeze_rejection_report_20260816.md": (
        "a24ce77e64d9051f676110212d2d3151cb76e2aa604818aac1a9a61bf559a692"),
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _read_base() -> dict[str, bytes]:
    data = BASE_SOURCE.read_bytes()
    if _sha(data) != EXPECTED_BASE_SOURCE_SHA256:
        raise RuntimeError("Goal5790 exact Goal5785 source base drifted")
    payloads: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in payloads:
                raise RuntimeError(f"unsafe/duplicate base member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported base member: {member.name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts) \
                    or name.endswith((".pyc", "librtdl_optix.so")) \
                    or "/build/" in f"/{name}/":
                raise RuntimeError(f"private/prebuilt base member: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable base member: {member.name}")
            payloads[name] = stream.read()
    payloads.pop(OLD_SOURCE_MANIFEST, None)
    return payloads


def _overlay_names() -> tuple[str, ...]:
    names = set(FIXED_OVERLAYS)
    names.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts").glob("goal5790_*.py")
        if path.is_file()
    )
    names.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tests").glob("goal5790_*.py")
        if path.is_file()
    )
    # These are claim authority, not optional decoration.  A partial checkout
    # must fail rather than emit a bundle without the frozen Goal5789 calculus
    # or Goal5790 T0 Particle-exclusion decision.
    names.update(PROVENANCE_FILES)
    required = set(FIXED_OVERLAYS) | {
        "scripts/goal5790_home_functional_validation.py",
        "scripts/goal5790_home_ptx_producer_probe.py",
        "scripts/goal5790_recount_home_functional.py",
        "scripts/goal5790_home_clean_validate.py",
        "src/rtdsl/physical_execution_provenance.py",
        "tests/goal5790_fusion_ablation_contract_test.py",
        "tests/goal5790_operation_evidence_test.py",
        "tests/goal5790_deferred_traversal_evidence_test.py",
        "tests/goal5790_deferred_triangle_segment_evidence_test.py",
        "tests/goal5790_triangle_runtime_integration_test.py",
        "tests/goal5790_home_functional_harness_test.py",
        "tests/goal5790_static_formal_harness_test.py",
    } | set(PROVENANCE_FILES)
    missing = sorted(name for name in required if not (ROOT / name).is_file())
    if missing:
        raise FileNotFoundError(f"Goal5790 required overlay missing: {missing!r}")
    drift = sorted(
        name for name, expected in EXPECTED_PROVENANCE_SHA256.items()
        if _sha((ROOT / name).read_bytes()) != expected
    )
    if drift:
        raise RuntimeError(f"Goal5790 immutable provenance drifted: {drift!r}")
    return tuple(sorted(names))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--source-output", type=Path, required=True)
    parser.add_argument("--source-twin", type=Path, required=True)
    args = parser.parse_args()
    outputs = (args.output, args.twin, args.source_output, args.source_twin)
    if len({path.resolve() for path in outputs}) != len(outputs):
        raise ValueError("Goal5790 bundle/source outputs must be pairwise distinct")
    for path in outputs:
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)

    source_payloads = _read_base()
    overlays = _overlay_names()
    for name in overlays:
        source_payloads[name] = (ROOT / name).read_bytes()
    rows = [
        {"path": name, "size_bytes": len(data), "sha256": _sha(data)}
        for name, data in sorted(source_payloads.items())
    ]
    source_tree_sha = _sha(json.dumps(
        rows, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode())
    source_manifest = (json.dumps({
        "schema": "rtdl.goal5790.portable_source_manifest.v1",
        "run_goal_id": 5790,
        "base_source_sha256": EXPECTED_BASE_SOURCE_SHA256,
        "file_count": len(rows),
        "overlay_file_count": len(overlays),
        "source_tree_sha256": source_tree_sha,
        "files": rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    source_manifest_member = (
        "history/internal_docs/goal5790_portable_source_manifest.json"
    )
    source_payloads[source_manifest_member] = source_manifest
    source_bytes = _archive(source_payloads)

    validator = (ROOT / "scripts/goal5790_home_clean_validate.py").read_bytes()
    runner = (ROOT / "scripts/goal5790_home_functional_validation.py").read_bytes()
    recount = (ROOT / "scripts/goal5790_recount_home_functional.py").read_bytes()
    freeze = (ROOT / SHARED_FREEZE).read_bytes()
    expected_value_and_fallback = (ROOT / EXPECTED_VALUE_AND_FALLBACK).read_bytes()
    home_machine_authority = (ROOT / HOME_MACHINE_AUTHORITY).read_bytes()
    readme = (
        "# Goal5790 local functional fusion-ablation candidate\n\n"
        "This source-only candidate builds one fresh target-native OptiX "
        "provider, then runs ten functional/operation-evidence lanes for "
        "weighted Triangle RT-2A1 only: four small-fixture ON/OFF x "
        "cold/prepared lanes plus six untimed bounded-real ON/OFF smokes "
        "covering the frozen first 262,144 edge records of com-dblp, "
        "cit-Patents and soc-LiveJournal1 after each full input SHA is checked. "
        "The prefixes are functional views, not performance samples. Particle is excluded by "
        "the T0 kill gate. It creates no registered performance result and "
        "does not authorize a POD or compiler-fusion claim.\n\n"
        "Candidate v8 binds the exact lx1 CUDA 12.2 NVRTC, NVRTC builtins, "
        "NVVM and libdevice paths and SHA-256 identities; it performs real "
        "Numba and CuPy compilation probes and traces inspect-target producer "
        "opens while distinguishing actual producer binaries from benign "
        "Numba libdevice Python-module imports, and captures long producer "
        "paths without strace abbreviation. Candidates v4 through v7 are "
        "preserved terminal lineages and may "
        "never execute again.\n\n"
        "After extracting this outer archive, invoke the create-only validator "
        "with the exact bundle SHA, an absent work root, the Home Python, CUDA "
        "and OptiX prefixes, and the directory containing the three full "
        "frozen `.edge` files:\n\n"
        "```text\n"
        "python HARNESS/goal5790_home_clean_validate.py \\\n"
        "  --bundle <this-bundle.tar.gz> --expected-bundle-sha256 <sha256> \\\n"
        "  --work-root <new-empty-path> --python <python> \\\n"
        "  --cuda-prefix <cuda> --optix-prefix <optix> \\\n"
        "  --compute-capability 61 --triangle-data-root <triangle-data-dir>\n"
        "```\n"
    ).encode()
    outer_payloads = {
        "SOURCE.tar.gz": source_bytes,
        "HARNESS/goal5790_home_clean_validate.py": validator,
        "HARNESS/goal5790_home_functional_validation.py": runner,
        "HARNESS/goal5790_recount_home_functional.py": recount,
        "SHARED_CONTRACT_FREEZE.json": freeze,
        "EXPECTED_VALUE_AND_FALLBACK.json": expected_value_and_fallback,
        "HOME_MACHINE_AUTHORITY.json": home_machine_authority,
        "README.md": readme,
    }
    outer_rows = [
        {"path": name, "size_bytes": len(data), "sha256": _sha(data)}
        for name, data in sorted(outer_payloads.items())
    ]
    manifest = (json.dumps({
        "schema": "rtdl.goal5790.local_functional_candidate_manifest.v1",
        "goal": 5790,
        "bundle_version": 8,
        "superseded_candidate_v1_sha256": (
            "bd536a8cc48f5fad046ea536c74048aa8b8da5e702c8ab0e266f3b78c2b5a273"),
        "superseded_candidate_v1_executable": False,
        "supersession_reason": (
            "pre_freeze_candidate_precedes_final_toc_tou_and_home_identity_"
            "admission_hardening"),
        "superseded_candidate_v2_sha256": (
            "d52a0b36a5e4697b64832cd2ea4d462dd23bf126b5ef4962d504700690c8ccee"),
        "superseded_candidate_v2_executable": False,
        "candidate_v2_zero_worker_failure": (
            "cuda_12_2_rejected_default_gcc_13_before_native_build"),
        "candidate_v3_cuda_host_compiler_policy": (
            "exact_gxx12_identity_and_explicit_nvcc_ccbin"),
        "superseded_candidate_v3_sha256": (
            "3ff9edf87526b1937aaab815d59dee40556030c37646227ae879c682a303635e"),
        "superseded_candidate_v3_executable": False,
        "candidate_v3_zero_worker_failure": (
            "resolved_gxx12_symlink_changed_version_banner_identity"),
        "candidate_v4_native_build_preflight_sha256": (
            "93e63f7beabfda09673a9b0fa7e6379939f7d10adc38df80c37ff69a1b882aa9"),
        "superseded_candidate_v4_sha256": (
            "568a1b1f60b83f58e480bc50d3801d748391f4628bcf458113d9f03bb3aef1b1"),
        "superseded_candidate_v4_source_archive_sha256": (
            "eb3782e3fe2d14cd2749b52de4ab49b089833049a5d372215c5e27cc426e255c"),
        "superseded_candidate_v4_executable": False,
        "candidate_v4_zero_worker_failure": (
            "executing_runner_and_shipped_home_authority_schema_drift"),
        "candidate_v4_s3_native_sha256_preserved": False,
        "candidate_v4_s3_result_sha256": EXPECTED_PROVENANCE_SHA256[
            "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_result_20260816.json"],
        "candidate_v4_s3_report_sha256": EXPECTED_PROVENANCE_SHA256[
            "history/internal_docs/goal5790_v4_home_s3_zero_worker_failure_report_20260816.md"],
        "superseded_candidate_v5_sha256": (
            "fad98d8ace84a7e6fab592eab854b1dfce3e69997906f8032865a62bbe23022e"),
        "superseded_candidate_v5_source_archive_sha256": (
            "49be38c73bf2266750f1ea886e7417cfafc1f56399fd550c6221a45960b32f1b"),
        "superseded_candidate_v5_executable": False,
        "candidate_v5_prefreeze_rejection": (
            "missing_exact_nvrtc_builtins_and_actual_numba_producer_admission"),
        "candidate_v5_rejection_result_sha256": EXPECTED_PROVENANCE_SHA256[
            "history/internal_docs/goal5790_v5_prefreeze_rejection_result_20260816.json"],
        "candidate_v5_rejection_report_sha256": EXPECTED_PROVENANCE_SHA256[
            "history/internal_docs/goal5790_v5_prefreeze_rejection_report_20260816.md"],
        "superseded_candidate_v6_sha256": (
            "d70b94626d1879f67c6110d627850badf47b6956ea1459b4a770336881d973b3"),
        "superseded_candidate_v6_source_archive_sha256": (
            "78992214d62517f11dfe6faa2870e76227db46ef20955663bd0d5a3fc7148fe2"),
        "superseded_candidate_v6_executable": False,
        "candidate_v6_prefreeze_rejection": (
            "strace_prefix_classifier_misclassified_benign_numba_libdevice_python_modules"),
        "candidate_v6_rejection_result_sha256": EXPECTED_PROVENANCE_SHA256[
            "history/internal_docs/goal5790_v6_prefreeze_rejection_result_20260816.json"],
        "candidate_v6_rejection_report_sha256": EXPECTED_PROVENANCE_SHA256[
            "history/internal_docs/goal5790_v6_prefreeze_rejection_report_20260816.md"],
        "superseded_candidate_v7_sha256": (
            "228a18ca968c914525b570ae3c33d162435a5c05b2ccc3dd9741d3efe788af13"),
        "superseded_candidate_v7_source_archive_sha256": (
            "41776518619a999e525652ee099337d10289135507338d3cf639c9f833c88d9e"),
        "superseded_candidate_v7_executable": False,
        "candidate_v7_prefreeze_rejection": (
            "strace_default_string_limit_truncated_exact_cuda_producer_paths"),
        "candidate_v7_rejection_result_sha256": EXPECTED_PROVENANCE_SHA256[
            "history/internal_docs/goal5790_v7_prefreeze_rejection_result_20260816.json"],
        "candidate_v7_rejection_report_sha256": EXPECTED_PROVENANCE_SHA256[
            "history/internal_docs/goal5790_v7_prefreeze_rejection_report_20260816.md"],
        "candidate_v8_ptx_producer_policy": (
            "exact_lx1_cuda_12_2_nvrtc_builtins_nvvm_libdevice_compile_and_open_audit"),
        "source_base_goal_id": 5785,
        "source_archive_sha256": _sha(source_bytes),
        "source_manifest_sha256": _sha(source_manifest),
        "source_tree_sha256": source_tree_sha,
        "shared_contract_freeze_file_sha256": _sha(freeze),
        "expected_value_and_fallback_sha256": _sha(
            expected_value_and_fallback),
        "home_machine_authority_sha256": _sha(home_machine_authority),
        "source_file_count": len(source_payloads),
        "overlay_file_count": len(overlays),
        "retained_mechanism_count": 1,
        "paper_algorithm": "RT-2A1",
        "particle_included": False,
        "home_functional_lane_count": 10,
        "home_small_fixture_lane_count": 4,
        "home_bounded_real_smoke_lane_count": 6,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "source_free_of_private_codex_state": True,
        "source_free_of_prebuilt_target_native": True,
        "pod_or_target_execution_authorized": False,
        "compiler_fusion_claim_authorized": False,
        "payload_count": len(outer_rows),
        "payload_bytes": sum(row["size_bytes"] for row in outer_rows),
        "payloads": outer_rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    outer_payloads["PORTABLE_MANIFEST.json"] = manifest
    bundle = _archive(outer_payloads)

    for path, data in (
        (args.output, bundle), (args.twin, bundle),
        (args.source_output, source_bytes), (args.source_twin, source_bytes),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if args.output.read_bytes() != args.twin.read_bytes() \
            or args.source_output.read_bytes() != args.source_twin.read_bytes():
        raise RuntimeError("Goal5790 deterministic twin differs")
    print(json.dumps({
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": _sha(source_bytes),
        "source_manifest_sha256": _sha(source_manifest),
        "source_tree_sha256": source_tree_sha,
        "source_file_count": len(source_payloads),
        "overlay_file_count": len(overlays),
        "bundle_twin_byte_identical": True,
        "source_twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
