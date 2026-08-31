#!/usr/bin/env python3
"""Build the deterministic Goal5769 v33 pre-POD successor and twin."""

from __future__ import annotations

import fnmatch
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "history/internal_docs/goal5768_three_way_pre_pod_bundle_v9_20260812.tar.gz"
TOOLCHAIN_BASE = ROOT / "history/internal_docs/goal5749_modern_rtx_bundle_v3_20260811.tar.gz"
EXTRA_WHEELHOUSE = ROOT / "history/internal_docs/goal5769_linux_wheelhouse_20260812"
OUTPUT = ROOT / "history/internal_docs/goal5769_three_way_pre_pod_bundle_v33_20260813.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5769_three_way_pre_pod_bundle_v33_twin_20260813.tar.gz"

OVERLAYS = (
    "scripts/goal5768_target_prepare.py",
    "scripts/goal5768_three_way_frontdoors.py",
    "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
    "scripts/goal5769_pre_pod_admission.py",
    "scripts/goal5768_formal_controller.py",
    "scripts/goal5768_three_way_worker.py",
    "scripts/goal5757_verify_core_freeze.py",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/rtdsl/canonical_physical_resolution.py",
    "src/rtdsl/default_compiler_frontdoor.py",
    "src/rtdsl/default_physical_selection.py",
    "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
    "Paper-reproduction-apps/rtdl3_whole_app_contract.py",
    "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py",
    "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py",
    "Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py",
    "history/internal_docs/goal5769_v4_core_successor_manifest_20260812.json",
    "tests/goal5751_v4_formal_native_runtime_static_test.py",
    "tests/goal5761_v4_multiround_spatial_test.py",
    "tests/goal5756_v4_builtin_triangle_runtime_test.py",
    "tests/goal5768_pre_pod_bundle_test.py",
    "tests/goal5768_three_way_frontdoors_test.py",
    "tests/goal5768_formal_harness_test.py",
    "tests/goal5769_pre_pod_admission_test.py",
    "tests/goal5769_v4_pre_pod_admission_test.py",
)

DISCOVERY = (
    {"pattern": "goal57*_v4_*test.py", "expected_test_case_count": 201},
    {"pattern": "goal5768_*test.py", "expected_test_case_count": 22},
    {"pattern": "goal5769_*test.py", "expected_test_case_count": 30},
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _outer_payloads(path: Path) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported outer member: {member.name}")
            name = PurePosixPath(member.name).as_posix()
            if name.startswith("/") or ".." in PurePosixPath(name).parts \
                    or name in payloads:
                raise RuntimeError(f"unsafe/duplicate outer member: {name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable outer member: {name}")
            payloads[name] = handle.read()
    return payloads


def _source_payloads(source_bytes: bytes) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(source_bytes), mode="r:gz") as source:
        for member in source.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            if not parts or path.is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe source member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported source member: {member.name}")
            name = "/".join(parts)
            if name in payloads:
                raise RuntimeError(f"duplicate source member: {name}")
            handle = source.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable source member: {name}")
            payloads[name] = handle.read()
    return payloads


def _toolchain_payloads() -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    with tarfile.open(TOOLCHAIN_BASE, "r:gz") as archive:
        for member in archive.getmembers():
            source_name = PurePosixPath(member.name).as_posix()
            if source_name == "payload/optix9_include.tar.gz":
                target_name = "TOOLCHAIN/optix9_include.tar.gz"
            elif source_name.startswith("payload/cuda_debs/"):
                target_name = "TOOLCHAIN/cuda_debs/" + PurePosixPath(source_name).name
            elif source_name.startswith("payload/wheelhouse/") and any(
                token in PurePosixPath(source_name).name
                for token in ("llvmlite-0.47.0", "numba-0.65.1", "numpy-2.2.6",
                              "nvidia_cuda_nvcc_cu12-12.8.93",
                              "nvidia_cuda_nvrtc_cu12-12.8.93",
                              "nvidia_cuda_runtime_cu12-12.8.90")
            ):
                target_name = "TOOLCHAIN/wheelhouse/" + PurePosixPath(source_name).name
            else:
                continue
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable Goal5749 toolchain member: {source_name}")
            payloads[target_name] = handle.read()
    for pattern in ("cupy_cuda12x-14.0.1-*.whl", "cuda_pathfinder-1.3.3-*.whl"):
        matches = sorted(EXTRA_WHEELHOUSE.glob(pattern))
        if len(matches) != 1:
            raise RuntimeError(f"Goal5769 wheelhouse mismatch: {pattern}")
        path = matches[0]
        payloads[f"TOOLCHAIN/wheelhouse/{path.name}"] = path.read_bytes()
    return payloads


def _row(name: str, data: bytes) -> dict[str, object]:
    return {"path": name, "sha256": _sha(data), "size_bytes": len(data)}


def main() -> None:
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
    base = _outer_payloads(BASE)
    source_payloads = _source_payloads(base["SOURCE.tar.gz"])
    for name in OVERLAYS:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        source_payloads[name] = path.read_bytes()
    source = _archive(source_payloads)

    test_names: set[str] = set()
    for row in DISCOVERY:
        test_names.update(
            name for name in source_payloads
            if name.startswith("tests/")
            and fnmatch.fnmatch(PurePosixPath(name).name, row["pattern"]))
    test_rows = [_row(name, source_payloads[name]) for name in sorted(test_names)]
    test_manifest = {
        "schema": "rtdl.goal5769.exact_test_manifest.v1",
        "goal": 5769,
        "files": test_rows,
        "discovery_patterns": list(DISCOVERY),
        "missing_or_extra_test_file_fails_closed": True,
        "unexpected_test_case_count_fails_closed": True,
    }
    test_manifest_bytes = (
        json.dumps(test_manifest, indent=2, sort_keys=True) + "\n").encode()

    toolchain = _toolchain_payloads()
    toolchain_rows = [_row(name, data) for name, data in sorted(toolchain.items())]
    toolchain_policy = {
        "schema": "rtdl.goal5769.target_toolchain_policy.v1",
        "goal": 5769,
        "policy_kind": "append_only_successor_of_goal5749_actual_v4_matrix",
        "python_executable": "/usr/bin/python3.12",
        "versions": {
            "python": "3.12.3", "numba": "0.65.1", "numpy": "2.2.6",
            "llvmlite": "0.47.0", "cupy": "14.0.1",
            "cuda_toolkit": "12.8", "cuda_nvcc": "12.8.93",
            "cuda_runtime": "12.8.90", "optix_sdk": "9.0.0",
        },
        "cuda_and_optix_are_bundled_not_target_mutable": True,
        "python_packages_installed_no_index_no_deps": True,
        "exact_driver_is_owner_authority_bound_and_execution_observed": True,
        "payloads": toolchain_rows,
    }
    toolchain_policy_bytes = (
        json.dumps(toolchain_policy, indent=2, sort_keys=True) + "\n").encode()

    harness = (ROOT / "scripts/goal5768_target_prepare.py").read_bytes()
    admission = (ROOT / "scripts/goal5769_pre_pod_admission.py").read_bytes()
    readme = (
        "# Goal5769 V2/V3/V4 pre-POD successor v33\n\n"
        "This candidate supersedes rejected Goal5769 v24 after the target "
        "exposed nonportable equal-distance primitive ownership in the two "
        "new particle comparison backports.  V25 adds only their exact, "
        "timer-included local-topology owner and adversarial tests. It requires real "
        "file-backed owner-returned external review and absorption bytes, "
        "carries the exact Python partner/CUDA/OptiX toolchain, validates exact "
        "test membership and cardinality, and can execute only a create-only "
        "39-lane functional prepare. Stage B remains impossible without a second "
        "owner authority. No performance result exists.\n"
    ).encode()

    outer: dict[str, bytes] = {
        "SOURCE.tar.gz": source,
        "HARNESS/goal5768_target_prepare.py": harness,
        "HARNESS/goal5769_pre_pod_admission.py": admission,
        "POLICY/EXACT_TEST_MANIFEST.json": test_manifest_bytes,
        "TOOLCHAIN/TOOLCHAIN_POLICY.json": toolchain_policy_bytes,
        "README.md": readme,
        **toolchain,
    }
    rows = [_row(name, data) for name, data in sorted(outer.items())]
    manifest = {
        "schema": "rtdl.goal5769.three_way_pre_pod_manifest.v1",
        "goal": 5769,
        "bundle_version": 33,
        "supersedes_rejected_goal5768_v9": True,
        "supersedes_goal5769_v10_wrong_clean_test_cardinality": True,
        "supersedes_goal5769_v11_stage_b_string_only_review_gate": True,
        "supersedes_goal5769_v12_concurrent_source_mutation_during_build": True,
        "supersedes_goal5769_v13_stale_canonical_provider_source_pins": True,
        "supersedes_goal5769_v14_unbound_direct_grouped_i64_optix_launch": True,
        "supersedes_goal5769_v15_second_stale_default_compiler_source_pin": True,
        "supersedes_goal5769_v16_missing_shared_v3_app_driver_contract": True,
        "supersedes_goal5769_v17_missing_xhd_historical_route_dependencies": True,
        "supersedes_goal5769_v18_import_gate_module_name_collision": True,
        "supersedes_goal5769_v19_unbound_prepared_closest_hit_launch": True,
        "supersedes_goal5769_v20_unbound_direct_closest_hit_launch": True,
        "supersedes_goal5769_v21_nondeterministic_equal_distance_triangle_tie": True,
        "supersedes_goal5769_v22_builtin_triangle_edge_owner_not_enumerable": True,
        "supersedes_goal5769_v23_stage_a_inprocess_source_src_not_bootstrapped": True,
        "supersedes_goal5769_v24_particle_backport_nonportable_equal_distance_owner": True,
        "supersedes_goal5769_v25_external_review_only_gate_conflicted_with_owner_final_review_directive": True,
        "supersedes_goal5769_v26_incomplete_declared_source_delta": True,
        "supersedes_goal5769_v27_unenforced_exact_gpu_uuid": True,
        "supersedes_goal5769_v28_owner_direct_result_relabelled_as_external_review": True,
        "supersedes_goal5769_v29_formal_worker_partner_environment_not_propagated": True,
        "supersedes_goal5769_v30_stale_owner_direct_source_delta_gate": True,
        "supersedes_goal5769_v31_admission_tests_not_in_target_test_discovery": True,
        "supersedes_goal5769_v32_stale_two_pattern_manifest_validator": True,
        "owner_direct_result_uses_neutral_authorization_fields": True,
        "exact_gpu_uuid_is_mechanically_admitted_before_worker_zero": True,
        "owner_direct_successor_requires_exact_delta_and_strict_internal_review": True,
        "owner_direct_execution_never_claims_external_preexecution_review": True,
        "goal5769_v24_stage_a_failure_archive_sha256": (
            "803130206396a69128f485afe20933a990b1cecc7e52a3f6155abf6321de40a9"),
        "v4_product_or_native_changed_by_v25": False,
        "particle_predecessor_topology_owner_inside_complete_timer": True,
        "particle_all_triangle_oracle_used_as_output": False,
        "target_fixed_radius_evidence_is_regenerated_before_functional_smoke": True,
        "base_goal5768_v9_sha256": _sha(BASE.read_bytes()),
        "source_archive_sha256": _sha(source),
        "source_file_count": len(source_payloads),
        "toolchain_policy_sha256": _sha(toolchain_policy_bytes),
        "test_manifest_sha256": _sha(test_manifest_bytes),
        "owner_review_is_file_backed": True,
        "prepare_is_create_only": True,
        "functional_smoke_worker_count": 39,
        "fixed_radius_refinement_functional_case_count": 17,
        "formal_worker_count": 0,
        "registered_formal_timing_count": 0,
        "formal_requires_second_exact_owner_authority": True,
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["size_bytes"]) for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    outer["PORTABLE_MANIFEST.json"] = manifest_bytes
    bundle = _archive(outer)
    OUTPUT.write_bytes(bundle)
    TWIN.write_bytes(bundle)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("Goal5769 v33 twin differs")
    print(json.dumps({
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": _sha(source),
        "toolchain_policy_sha256": _sha(toolchain_policy_bytes),
        "test_manifest_sha256": _sha(test_manifest_bytes),
        "source_file_count": len(source_payloads),
        "outer_payload_count": len(rows),
        "outer_payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
