#!/usr/bin/env python3
"""Clean Home-Linux functional closure for the exact Goal5790 candidate.

This outer harness is create-only.  It rebuilds a target-local native, seals a
target-materialization authority, runs ten fresh-process functional lanes, and
invokes the independent raw recount.  The four small lanes cover ON/OFF x
cold/prepared.  Six untimed bounded-real smokes cover ON/OFF for each of the
three frozen Triangle datasets.  It never creates a registered timing or
target-performance claim.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import struct
import subprocess
import tarfile


PREFIX_EDGE_RECORD_COUNT = 262_144
REAL_DATASETS = {
    "com-dblp": {
        "filename": "com-dblp.edge",
        "sha256": "e9647564c1ca96589cc52314cabf5569ec80b9f5d697578a55d47fbe7aafca67",
        "size_bytes": 8_398_928,
        "prefix_sha256": "0a6d9608bd843e12ca1bac1d93a49e06cd40d76ab0526735dbf7204e6586be14",
        "prefix_triangle_count": 159_861,
    },
    "cit-Patents": {
        "filename": "cit-Patents.edge",
        "sha256": "c5b2c9203eeabb46414965755c33befdb1810e71cb51155eb940a68a6179d855",
        "size_bytes": 132_151_584,
        "prefix_sha256": "4b2b992c8efc9b67d6695245eb5d4647e39a9a1d996d4b05078f870dd1847ba0",
        "prefix_triangle_count": 97,
    },
    "soc-LiveJournal1": {
        "filename": "soc-LiveJournal1.edge",
        "sha256": "80199ecebb7ebdf3b4861748e009d16b1c5f93c35eba837a7ce37f94ada35f83",
        "size_bytes": 551_950_184,
        "prefix_sha256": "86c12ecc87289f9fec53bf6f11f8607fde3d8b8380917a45dd6609fd26b4e8d1",
        "prefix_triangle_count": 70_758,
    },
}
REAL_PREFIX_RULE = (
    "first_262144_little_endian_i32_pair_records_preserve_order"
)
HOME_MACHINE_AUTHORITY = {
    "schema": "rtdl.goal5790.frozen_home_machine_authority.v3",
    "execution_environment_class": "HOME_PASCAL_FUNCTIONAL_ONLY",
    "gpu_name": "NVIDIA GeForce GTX 1070",
    "gpu_uuid": "GPU-8e04454e-c177-6e5b-3f43-e676980ecdfa",
    "driver_version": "580.126.09",
    "compute_capability": "6.1",
    "cuda_nvcc_version": "Build cuda_12.2.r12.2/compiler.33191640_0",
    "cuda_host_compiler_path": "/usr/bin/g++-12",
    "cuda_host_compiler_version": (
        "g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0"
    ),
    "cuda_nvrtc_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
        "libnvrtc.so.12.2.140"
    ),
    "cuda_nvrtc_sha256": (
        "000ca6278ba8b32a7dac383eb7440929c5a09095b43dd5f2df3911f63520db70"
    ),
    "cuda_nvrtc_builtins_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
        "libnvrtc-builtins.so.12.2.140"
    ),
    "cuda_nvrtc_builtins_sha256": (
        "968ebb00640e461f587ad96d01735ac85bf4b2ab4d1cb35b3b489c3cf2cc7f18"
    ),
    "cuda_nvrtc_runtime_version": [12, 2],
    "cuda_nvvm_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/nvvm/lib64/libnvvm.so.4.0.0"
    ),
    "cuda_nvvm_sha256": (
        "b69eaddcce6a063361f2d172ed535c3d6f7ae494a40c6ffdb7de024f89dbf80a"
    ),
    "cuda_libdevice_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/nvvm/libdevice/libdevice.10.bc"
    ),
    "cuda_libdevice_sha256": (
        "5c9f80bf689d5d0e67dabf914a2a865a3d8b8c5ff86b86c46f63c3bb067ca523"
    ),
    "cuda_toolkit_resolved_path": "/home/lestat/vendor/cuda-12.2.2",
    "modern_rtx_execution_authorized": False,
    "pod_used": False,
}


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ensure_ascii=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(
    command: list[str], *, cwd: Path, env: dict[str, str], log: Path,
) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode:
        raise RuntimeError(f"command failed: {command!r}; see {log}")
    return completed.stdout


def _safe_extract(archive: Path, target: Path) -> list[str]:
    names: list[str] = []
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in names:
                raise RuntimeError(f"unsafe/duplicate archive member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported archive member: {member.name}")
            destination = target.joinpath(*parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            stream = handle.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            destination.write_bytes(stream.read())
            names.append(name)
    return names


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _write_k4(path: Path) -> None:
    edges = (
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3), (2, 3),
    )
    path.write_bytes(b"".join(struct.pack("<ii", left, right)
                              for left, right in edges))


def _write_bounded_prefix(source: Path, target: Path) -> bytes:
    with source.open("rb") as stream:
        payload = stream.read(PREFIX_EDGE_RECORD_COUNT * 8)
    if len(payload) != PREFIX_EDGE_RECORD_COUNT * 8:
        raise RuntimeError(f"Triangle full input is too short for bounded view: {source}")
    target.write_bytes(payload)
    return payload


def _verify_home_authority(path: Path, gpu_csv: str) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = dict(HOME_MACHINE_AUTHORITY)
    expected["receipt_sha256"] = _digest(HOME_MACHINE_AUTHORITY)
    if value != expected:
        raise RuntimeError("Goal5790 frozen Home-machine authority drift")
    rows = list(csv.reader(gpu_csv.splitlines()))
    if len(rows) != 1 or len(rows[0]) != 4:
        raise RuntimeError("Goal5790 requires exactly one admitted Home GPU")
    observed = tuple(field.strip() for field in rows[0])
    exact = (
        expected["gpu_name"], expected["gpu_uuid"],
        expected["driver_version"], expected["compute_capability"],
    )
    if observed != exact:
        raise RuntimeError(
            f"Goal5790 rejects non-Home GPU identity: {observed!r}")
    return expected


def _verify_home_ptx_toolchain_files(
    authority: dict[str, object],
) -> dict[str, object]:
    """Rehash the three exact lx1 PTX producers before any Python compile."""
    observed: dict[str, object] = {}
    for stem in (
        "cuda_nvrtc", "cuda_nvrtc_builtins", "cuda_nvvm", "cuda_libdevice",
    ):
        path_field = f"{stem}_resolved_path"
        sha_field = f"{stem}_sha256"
        expected_path = str(authority[path_field])
        path = Path(expected_path)
        if not path.is_file() or str(path.resolve()) != expected_path:
            raise RuntimeError(f"Goal5790 exact PTX producer path drift: {stem}")
        observed[path_field] = str(path.resolve())
        observed[sha_field] = _sha(path)
        if observed[sha_field] != authority[sha_field]:
            raise RuntimeError(f"Goal5790 exact PTX producer SHA drift: {stem}")
    return observed


def _verify_home_nvrtc_runtime(
    authority: dict[str, object], versions: dict[str, object],
) -> None:
    if versions.get("cupy_nvrtc_runtime_version") \
            != authority["cuda_nvrtc_runtime_version"]:
        raise RuntimeError("Goal5790 CuPy NVRTC runtime version drift")
    exact_nvrtc = sorted((
        str(authority["cuda_nvrtc_resolved_path"]),
        str(authority["cuda_nvrtc_builtins_resolved_path"]),
    ))
    if versions.get("loaded_nvrtc_family_paths") != exact_nvrtc:
        raise RuntimeError("Goal5790 loaded NVRTC-family path drift")
    toolkit = str(authority["cuda_toolkit_resolved_path"])
    if versions.get("cuda_home") != toolkit or versions.get("cuda_path") != toolkit:
        raise RuntimeError("Goal5790 CUDA_HOME/CUDA_PATH producer selector drift")
    if (
        versions.get("schema")
            != "rtdl.goal5790.home_ptx_producer_observation.v1"
        or
        versions.get("numba_selected_nvvm_by") != "CUDA_HOME"
        or versions.get("numba_selected_nvvm_path")
            != authority["cuda_nvvm_resolved_path"]
        or versions.get("numba_selected_nvvm_sha256")
            != authority["cuda_nvvm_sha256"]
        or versions.get("numba_selected_libdevice_by") != "CUDA_HOME"
        or versions.get("numba_selected_libdevice_path")
            != authority["cuda_libdevice_resolved_path"]
        or versions.get("numba_selected_libdevice_sha256")
            != authority["cuda_libdevice_sha256"]
        or versions.get("loaded_nvvm_paths")
            != [authority["cuda_nvvm_resolved_path"]]
        or versions.get("nvrtc_probe_output") != 5790
        or versions.get("elapsed_values_recorded") is not False
        or versions.get("application_input_used") is not False
        or versions.get("registered_performance_timing_created") is not False
    ):
        raise RuntimeError("Goal5790 observed PTX producer authority drift")


def _verify_ptx_program_inspection(inspection: dict[str, object]) -> str:
    value = inspection.get("ptx_program_identity")
    claimed = inspection.get("ptx_program_identity_sha256")
    if not isinstance(value, dict) or _digest(value) != claimed:
        raise RuntimeError("Goal5790 PTX program identity digest drift")
    if set(value) != {
        "schema", "wrapper", "ordered_leaves", "composed",
        "composer_leaf_bindings",
        "wrapper_leaf_composed_directive_equality_verified",
    } or value.get("schema") != "rtdl.goal5790.ptx_program_identity.v1" \
            or value.get("wrapper_leaf_composed_directive_equality_verified") \
                is not True:
        raise RuntimeError("Goal5790 PTX program identity schema drift")
    wrapper = value.get("wrapper")
    composed = value.get("composed")
    leaves = value.get("ordered_leaves")
    bindings = value.get("composer_leaf_bindings")
    if not isinstance(wrapper, dict) or not isinstance(composed, dict) \
            or not isinstance(leaves, list) or not leaves \
            or not isinstance(bindings, list) or len(bindings) != len(leaves):
        raise RuntimeError("Goal5790 PTX identity structure drift")
    common = composed.get("directives")
    if not isinstance(common, dict) \
            or set(common) != {"version", "target", "address_size"} \
            or common.get("target") != "sm_61" \
            or common.get("address_size") != "64" \
            or wrapper.get("directives") != common \
            or composed.get("ptx_sha256") \
                != inspection.get("composed_program_sha256"):
        raise RuntimeError("Goal5790 PTX wrapper/composed identity drift")
    for index, leaf in enumerate(leaves):
        if not isinstance(leaf, dict) \
                or set(leaf) != {"role", "abi_name", "ptx_sha256", "directives"} \
                or leaf.get("directives") != common \
                or bindings[index] != [leaf.get("role"), leaf.get("abi_name")]:
            raise RuntimeError("Goal5790 PTX leaf identity drift")
    if inspection.get("ptx_producer_observation", {}).get(
            "numba_probe_ptx_directives") != common:
        raise RuntimeError("Goal5790 probe/program PTX directives differ")
    return str(claimed)


def _verify_strace_producer_opens(
    trace_path: Path, authority: dict[str, object],
) -> dict[str, object]:
    successful: set[str] = set()
    for line in trace_path.read_text(encoding="utf-8", errors="strict").splitlines():
        match = re.search(
            r'openat\([^,]+,\s*"([^"]+)".*\)\s+=\s+([0-9]+)', line)
        if match and match.group(1).startswith("/"):
            successful.add(str(Path(match.group(1)).resolve()))
    expected = {
        str(Path(str(authority[field])).resolve()) for field in (
            "cuda_nvrtc_resolved_path", "cuda_nvrtc_builtins_resolved_path",
            "cuda_nvvm_resolved_path", "cuda_libdevice_resolved_path",
        )
    }
    # Classify only binary PTX producers.  Numba legitimately imports Python
    # modules such as ``libdevice.pyc``, ``libdevicedecl.pyc`` and
    # ``libdevicefuncs.pyc`` while compiling.  Prefix matching those module
    # names would falsely report a foreign producer even though the only
    # opened bitcode is the exact frozen ``libdevice.10.bc``.
    def is_producer_binary(path: str) -> bool:
        name = Path(path).name
        return bool(
            re.fullmatch(r"libnvrtc(?:-builtins)?\.so(?:\..+)?", name)
            or re.fullmatch(r"libnvvm\.so(?:\..+)?", name)
            or (name.startswith("libdevice") and name.endswith(".bc"))
        )

    producer_opens = {path for path in successful if is_producer_binary(path)}
    if not expected.issubset(producer_opens):
        raise RuntimeError(
            "Goal5790 inspect-target did not open every exact PTX producer")
    foreign = sorted(producer_opens - expected)
    if foreign:
        raise RuntimeError(
            f"Goal5790 inspect-target opened foreign PTX producers: {foreign!r}")
    return {
        "successful_exact_producer_opens": sorted(expected),
        "foreign_successful_producer_opens": [],
        "trace_sha256": _sha(trace_path),
    }


def _triangle_count(payload: bytes) -> int:
    if not payload or len(payload) % 8:
        raise RuntimeError("bounded Triangle input is not an i32-pair stream")
    edges: set[tuple[int, int]] = set()
    for left, right in struct.iter_unpack("<ii", payload):
        if left < 0 or right < 0:
            raise RuntimeError("bounded Triangle input contains negative vertex ID")
        if left != right:
            edges.add((min(left, right), max(left, right)))
    adjacency: dict[int, set[int]] = {}
    for left, right in edges:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    total = 0
    for left, right in edges:
        total += sum(1 for third in adjacency[left].intersection(adjacency[right])
                     if third > right)
    return total


def _verify_outer(outer: Path, names: list[str]) -> dict[str, object]:
    manifest = json.loads(
        (outer / "PORTABLE_MANIFEST.json").read_text(encoding="utf-8"))
    rows = {str(row["path"]): row for row in manifest["payloads"]}
    if set(names) != set(rows) | {"PORTABLE_MANIFEST.json"}:
        raise RuntimeError("Goal5790 outer bundle membership mismatch")
    if manifest.get("payload_count") != len(rows) or manifest.get(
            "payload_bytes") != sum(int(row["size_bytes"]) for row in rows.values()):
        raise RuntimeError("Goal5790 outer payload count/byte total drift")
    for name, row in rows.items():
        path = outer / name
        if path.stat().st_size != int(row["size_bytes"]) \
                or _sha(path) != row["sha256"]:
            raise RuntimeError(f"Goal5790 outer payload mismatch: {name}")
    required = {
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
        "candidate_v4_s3_result_sha256": (
            "6428ba811905081561ac01d3ebd0a390b57fad37880f49d63acff0e0eda1ce1c"),
        "candidate_v4_s3_report_sha256": (
            "163565c96ea37abc86f7b43bc8de25b46748982d98485bc62b891e22ff106dc9"),
        "superseded_candidate_v5_sha256": (
            "fad98d8ace84a7e6fab592eab854b1dfce3e69997906f8032865a62bbe23022e"),
        "superseded_candidate_v5_source_archive_sha256": (
            "49be38c73bf2266750f1ea886e7417cfafc1f56399fd550c6221a45960b32f1b"),
        "superseded_candidate_v5_executable": False,
        "candidate_v5_prefreeze_rejection": (
            "missing_exact_nvrtc_builtins_and_actual_numba_producer_admission"),
        "candidate_v5_rejection_result_sha256": (
            "5bf0a288af9ae27a06b83b03cc2b115de5a2a3b5b26e618843ab86369fa567bc"),
        "candidate_v5_rejection_report_sha256": (
            "b60f5f807a60075ce467e949b0d45d1a1173d1109974ab8396a5feae45671bc4"),
        "superseded_candidate_v6_sha256": (
            "d70b94626d1879f67c6110d627850badf47b6956ea1459b4a770336881d973b3"),
        "superseded_candidate_v6_source_archive_sha256": (
            "78992214d62517f11dfe6faa2870e76227db46ef20955663bd0d5a3fc7148fe2"),
        "superseded_candidate_v6_executable": False,
        "candidate_v6_prefreeze_rejection": (
            "strace_prefix_classifier_misclassified_benign_numba_libdevice_python_modules"),
        "candidate_v6_rejection_result_sha256": (
            "c934e12de5585b14ed382da9d2416b1ab452bdf2450a2d686d778737b364312f"),
        "candidate_v6_rejection_report_sha256": (
            "7ce28260985ba3ddcc500c25837d30186f9de929e9e53007b3bd4d0fb4eff248"),
        "superseded_candidate_v7_sha256": (
            "228a18ca968c914525b570ae3c33d162435a5c05b2ccc3dd9741d3efe788af13"),
        "superseded_candidate_v7_source_archive_sha256": (
            "41776518619a999e525652ee099337d10289135507338d3cf639c9f833c88d9e"),
        "superseded_candidate_v7_executable": False,
        "candidate_v7_prefreeze_rejection": (
            "strace_default_string_limit_truncated_exact_cuda_producer_paths"),
        "candidate_v7_rejection_result_sha256": (
            "4c19439962519e9884381701d7580874528f7d9986fcd5fbfdc78d8204aa6504"),
        "candidate_v7_rejection_report_sha256": (
            "a24ce77e64d9051f676110212d2d3151cb76e2aa604818aac1a9a61bf559a692"),
        "candidate_v8_ptx_producer_policy": (
            "exact_lx1_cuda_12_2_nvrtc_builtins_nvvm_libdevice_compile_and_open_audit"),
        "retained_mechanism_count": 1,
        "paper_algorithm": "RT-2A1",
        "home_functional_lane_count": 10,
        "home_small_fixture_lane_count": 4,
        "home_bounded_real_smoke_lane_count": 6,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "particle_included": False,
        "source_free_of_private_codex_state": True,
        "source_free_of_prebuilt_target_native": True,
        "pod_or_target_execution_authorized": False,
        "compiler_fusion_claim_authorized": False,
    }
    if any(manifest.get(key) != value for key, value in required.items()):
        raise RuntimeError("Goal5790 outer scope drift")
    return manifest


def _verify_source(source: Path, names: list[str]) -> dict[str, object]:
    manifest_path = (
        source / "history/internal_docs/goal5790_portable_source_manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = {str(row["path"]): row for row in manifest["files"]}
    member = manifest_path.relative_to(source).as_posix()
    if set(names) != set(rows) | {member}:
        raise RuntimeError("Goal5790 source membership mismatch")
    if manifest.get("file_count") != len(rows) \
            or manifest.get("run_goal_id") != 5790 \
            or manifest.get("base_source_sha256") \
                != "d1461498742e03a001662975b4ebb4dadb145d2a3027675c24f576c1b97c02d6":
        raise RuntimeError("Goal5790 source manifest identity/count drift")
    for name, row in rows.items():
        path = source / name
        if path.stat().st_size != int(row["size_bytes"]) \
                or _sha(path) != row["sha256"]:
            raise RuntimeError(f"Goal5790 source payload mismatch: {name}")
    reconstructed_tree = hashlib.sha256(json.dumps(
        list(manifest["files"]), sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode()).hexdigest()
    if reconstructed_tree != manifest["source_tree_sha256"]:
        raise RuntimeError("Goal5790 source-tree digest mismatch")
    forbidden = [name for name in names if (
        ".codex" in PurePosixPath(name).parts
        or ".git" in PurePosixPath(name).parts
        or "__pycache__" in PurePosixPath(name).parts
        or name.endswith((".pyc", "librtdl_optix.so"))
        or "/build/" in f"/{name}/"
    )]
    if forbidden:
        raise RuntimeError(f"Goal5790 source contains private/prebuilt files: {forbidden[:3]}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--expected-bundle-sha256", required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--cuda-prefix", type=Path, required=True)
    parser.add_argument("--optix-prefix", type=Path, required=True)
    parser.add_argument("--compute-capability", choices=("61",), default="61")
    parser.add_argument("--triangle-data-root", type=Path, required=True)
    parser.add_argument("--max-relation-rows", type=int, default=1_000_000)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    root = args.work_root.resolve()
    if root.exists() or root.is_symlink():
        raise FileExistsError(root)
    if _sha(bundle) != args.expected_bundle_sha256.lower():
        raise RuntimeError("Goal5790 bundle bytes changed")
    for path in (args.python, args.cuda_prefix, args.optix_prefix,
                 args.triangle_data_root):
        if not path.exists():
            raise FileNotFoundError(path)
    triangle_data_root = args.triangle_data_root.resolve()
    real_sources: dict[str, Path] = {}
    for dataset, identity in REAL_DATASETS.items():
        path = triangle_data_root / str(identity["filename"])
        if not path.is_file() or path.stat().st_size != identity["size_bytes"] \
                or _sha(path) != identity["sha256"]:
            raise RuntimeError(f"Goal5790 frozen Triangle input drifted: {dataset}")
        real_sources[dataset] = path
    if args.max_relation_rows != 1_000_000:
        raise ValueError("Goal5790 frozen relation bound must equal 1000000")

    root.mkdir(parents=True)
    logs = root / "logs"
    logs.mkdir()
    outer = root / "outer"
    outer.mkdir()
    outer_names = _safe_extract(bundle, outer)
    outer_manifest = _verify_outer(outer, outer_names)
    outer_rows = {
        str(row["path"]): row for row in outer_manifest["payloads"]
    }
    executing_harness_sha = _sha(Path(__file__).resolve())
    expected_harness_sha = outer_rows[
        "HARNESS/goal5790_home_clean_validate.py"]["sha256"]
    if executing_harness_sha != expected_harness_sha:
        raise RuntimeError(
            "executing Goal5790 clean validator differs from exact bundle")
    source = root / "source"
    source.mkdir()
    source_names = _safe_extract(outer / "SOURCE.tar.gz", source)
    source_manifest = _verify_source(source, source_names)
    if _sha(source / "scripts/goal5790_home_clean_validate.py") \
            != expected_harness_sha:
        raise RuntimeError(
            "outer/source Goal5790 clean validator identity mismatch")
    if (
        outer_manifest["source_archive_sha256"] != _sha(outer / "SOURCE.tar.gz")
        or outer_manifest["source_manifest_sha256"] != _sha(
            source / "history/internal_docs/goal5790_portable_source_manifest.json")
        or outer_manifest["source_tree_sha256"] != source_manifest["source_tree_sha256"]
        or outer_manifest["shared_contract_freeze_file_sha256"]
            != _sha(outer / "SHARED_CONTRACT_FREEZE.json")
        or outer_manifest["expected_value_and_fallback_sha256"]
            != _sha(outer / "EXPECTED_VALUE_AND_FALLBACK.json")
        or outer_manifest["home_machine_authority_sha256"]
            != _sha(outer / "HOME_MACHINE_AUTHORITY.json")
    ):
        raise RuntimeError("Goal5790 outer/source/freeze identity mismatch")
    preregistration = json.loads(
        (outer / "EXPECTED_VALUE_AND_FALLBACK.json").read_text(encoding="utf-8")
    )
    if (
        preregistration.get("goal") != 5790
        or preregistration.get("status")
            != "FROZEN_BEFORE_HOME_OR_TARGET_TIMING"
        or preregistration.get("scope", {}).get("independent_row_count") != 6
        or preregistration.get("comparison", {}).get("fixed_speedup_floor_used")
            is not False
        or preregistration.get("success_and_fallback", {}).get(
            "all_six_rows_must_be_retained") is not True
        or preregistration.get("governance", {}).get(
            "home_elapsed_values_may_change_this_authority") is not False
        or preregistration.get("governance", {}).get(
            "goal5791_target_execution_requires_separate_owner_authorization")
            is not True
    ):
        raise RuntimeError("Goal5790 expected-value/fallback authority drift")

    python = args.python.resolve()
    cuda = args.cuda_prefix.resolve()
    optix = args.optix_prefix.resolve()
    authority_file = outer / "HOME_MACHINE_AUTHORITY.json"
    unsigned_authority = dict(HOME_MACHINE_AUTHORITY)
    expected_authority = dict(unsigned_authority)
    expected_authority["receipt_sha256"] = _digest(unsigned_authority)
    if json.loads(authority_file.read_text(encoding="utf-8")) \
            != expected_authority:
        raise RuntimeError("Goal5790 frozen Home-machine authority drift")
    if str(cuda) != expected_authority["cuda_toolkit_resolved_path"]:
        raise RuntimeError("Goal5790 exact CUDA toolkit root drift")
    ptx_toolchain_files = _verify_home_ptx_toolchain_files(expected_authority)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((
        str(source / "src"), str(source), str(source / "scripts")))
    env["PATH"] = os.pathsep.join((str(cuda / "bin"), env.get("PATH", "")))
    env["CUDA_HOME"] = str(expected_authority["cuda_toolkit_resolved_path"])
    env["CUDA_PATH"] = str(expected_authority["cuda_toolkit_resolved_path"])
    env["LD_LIBRARY_PATH"] = os.pathsep.join((
        str(Path(str(expected_authority["cuda_nvvm_resolved_path"])).parent),
        str(Path(str(expected_authority["cuda_nvrtc_resolved_path"])).parent),
        "/usr/lib/x86_64-linux-gnu"))
    env["LD_PRELOAD"] = str(expected_authority["cuda_nvrtc_resolved_path"])
    env.pop("NUMBA_CUDA_NVVM", None)
    env.pop("NUMBA_CUDA_LIBDEVICE", None)
    for cache_name in (
        "RTDL_V4_FORMAL_LEAF_CACHE",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
    ):
        env.pop(cache_name, None)
    env["CUPY_CACHE_DIR"] = str(root / "fresh_cupy_probe_cache")
    env["RTDL_V4_CUDA_PREFIX"] = str(cuda)
    env["RTDL_V4_OPTIX_PREFIX"] = str(optix)
    versions = json.loads(_run([
        str(python),
        str(source / "scripts/goal5790_home_ptx_producer_probe.py"),
    ], cwd=source, env=env, log=logs / "ptx_producer_probe.log").strip())
    _verify_home_nvrtc_runtime(expected_authority, versions)
    gpu = _run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ], cwd=source, env=env, log=logs / "gpu.log").strip()
    home_machine_authority = _verify_home_authority(
        outer / "HOME_MACHINE_AUTHORITY.json", gpu)
    # Preserve the authorized symlink spelling.  Invoking the resolved target
    # changes GCC's version-banner program name and would falsely reject the
    # same compiler bytes before native build.
    host_compiler = Path(str(
        home_machine_authority["cuda_host_compiler_path"]))
    if not host_compiler.is_file() or not os.access(host_compiler, os.X_OK):
        raise RuntimeError("Goal5790 admitted CUDA host compiler is unavailable")
    host_compiler_version = _run(
        [str(host_compiler), "--version"], cwd=source, env=env,
        log=logs / "cuda_host_compiler.log").splitlines()[0].strip()
    if host_compiler_version != home_machine_authority[
            "cuda_host_compiler_version"]:
        raise RuntimeError("Goal5790 CUDA host compiler identity drift")
    nvcc = cuda / "bin/nvcc"
    nvcc_lines = _run(
        [str(nvcc), "--version"], cwd=source, env=env,
        log=logs / "nvcc.log").splitlines()
    if not nvcc_lines or nvcc_lines[-1].strip() != home_machine_authority[
            "cuda_nvcc_version"]:
        raise RuntimeError("Goal5790 nvcc identity drift")
    _run([
        "make", "build-optix", f"OPTIX_PREFIX={optix}", f"CUDA_PREFIX={cuda}",
        f"OPTIX_CUDA_ARCH=sm_{args.compute_capability}",
        f"CXX_OPTIX={nvcc} -ccbin {host_compiler}",
    ], cwd=source, env=env, log=logs / "build.log")
    native = source / "build/librtdl_optix.so"
    if not native.is_file():
        raise RuntimeError("fresh Goal5790 target native missing")
    env["RTDL_OPTIX_LIB"] = env["RTDL_OPTIX_LIBRARY"] = str(native)

    test_modules = (
        "tests.goal5790_deferred_traversal_evidence_test",
        "tests.goal5790_deferred_triangle_segment_evidence_test",
        "tests.goal5790_fusion_ablation_contract_test",
        "tests.goal5790_operation_evidence_test",
        "tests.goal5790_triangle_runtime_integration_test",
        "tests.goal5790_home_functional_harness_test",
        "tests.goal5790_static_formal_harness_test",
        "tests.goal5778_v4_checked_u64_device_reduction_test",
    )
    test_output = _run(
        [str(python), "-m", "unittest", *test_modules],
        cwd=source, env=env, log=logs / "focused_tests.log")

    inspect_path = root / "TARGET_PROGRAM_INSPECTION.json"
    runner = source / "scripts/goal5790_home_functional_validation.py"
    common = [
        str(python), str(runner), "--source-root", str(source),
        "--native", str(native), "--optix-include", str(optix / "include"),
        "--cuda-include", str(cuda / "include"),
        "--compute-capability", args.compute_capability,
        "--home-machine-authority", str(
            outer / "HOME_MACHINE_AUTHORITY.json"),
    ]
    strace_path = Path("/usr/bin/strace")
    if not strace_path.is_file() or not os.access(strace_path, os.X_OK):
        raise RuntimeError("Goal5790 requires /usr/bin/strace producer audit")
    producer_trace = logs / "inspect_target_producer_openat.log"
    _run([str(strace_path), "-f", "-s", "4096", "-e", "trace=openat", "-o",
          str(producer_trace), *common, *[
        "--mode", "inspect-target", "--output", str(inspect_path),
    ]], cwd=source, env=env, log=logs / "inspect_target.log")
    producer_open_audit = _verify_strace_producer_opens(
        producer_trace, home_machine_authority)
    inspection = json.loads(inspect_path.read_text(encoding="utf-8"))
    _verify_home_nvrtc_runtime(
        home_machine_authority, inspection.get("ptx_producer_observation", {}))
    ptx_program_identity_sha256 = _verify_ptx_program_inspection(inspection)
    if inspection.get("native_library_sha256") != _sha(native) \
            or inspection.get("provider_identity") != "optix" \
            or inspection.get("application_worker_executed") is not False \
            or inspection.get("home_machine_authority") \
                != home_machine_authority \
            or inspection.get("home_machine_authority_sha256") \
                != home_machine_authority["receipt_sha256"] \
            or inspection.get("ptx_producer_toolchain") != {
                field: home_machine_authority[field]
                for field in (
                    "cuda_nvrtc_resolved_path", "cuda_nvrtc_sha256",
                    "cuda_nvrtc_builtins_resolved_path",
                    "cuda_nvrtc_builtins_sha256",
                    "cuda_nvrtc_runtime_version",
                    "cuda_nvvm_resolved_path", "cuda_nvvm_sha256",
                    "cuda_libdevice_resolved_path", "cuda_libdevice_sha256",
                    "cuda_toolkit_resolved_path",
                )
            }:
        raise RuntimeError("Goal5790 target program inspection failed")

    target_evidence = root / "TARGET_MATERIALIZATION_EVIDENCE.tar.gz"
    target_evidence.write_bytes(_archive({
        "EXECUTION_SOURCE.tar.gz": (outer / "SOURCE.tar.gz").read_bytes(),
        "TARGET_NATIVE/librtdl_optix.so": native.read_bytes(),
        "TARGET_PROGRAM_INSPECTION.json": inspect_path.read_bytes(),
        "SOURCE_MANIFEST.json": (
            source / "history/internal_docs/goal5790_portable_source_manifest.json"
        ).read_bytes(),
        "SHARED_CONTRACT_FREEZE.json": (
            outer / "SHARED_CONTRACT_FREEZE.json").read_bytes(),
        "HOME_MACHINE_AUTHORITY.json": (
            outer / "HOME_MACHINE_AUTHORITY.json").read_bytes(),
        "PTX_PRODUCER_OPENAT_TRACE.log": producer_trace.read_bytes(),
        "PTX_PRODUCER_OBSERVATION.json": (
            json.dumps(versions, indent=2, sort_keys=True) + "\n").encode(),
        "PTX_PROGRAM_IDENTITY.json": (
            json.dumps(
                inspection["ptx_program_identity"], indent=2, sort_keys=True)
            + "\n").encode(),
    }))
    freeze_value = json.loads(
        (outer / "SHARED_CONTRACT_FREEZE.json").read_text(encoding="utf-8"))
    target_authority = {
        "schema": "rtdl.v4.target_materialization_authority.v2",
        "shared_contract_freeze_sha256": freeze_value[
            "shared_contract_freeze_sha256"],
        "execution_source_archive_sha256": _sha(outer / "SOURCE.tar.gz"),
        "execution_source_tree_sha256": source_manifest["source_tree_sha256"],
        "callback_ir_sha256": inspection["callback_ir_sha256"],
        "callback_authority_nonce": inspection["callback_authority_nonce"],
        "contract_sha256": inspection["contract_sha256"],
        "abi_sha256": inspection["abi_sha256"],
        "provider_identity": "optix",
        "program_bundle_identity": inspection["program_bundle_identity"],
        "composed_program_sha256": inspection["composed_program_sha256"],
        "cupy_version": inspection["cupy_version"],
        "fusion_on_downstream_operation_recipe": inspection[
            "fusion_on_downstream_operation_recipe"],
        "fusion_off_downstream_operation_recipe": inspection[
            "fusion_off_downstream_operation_recipe"],
        "fusion_on_downstream_operation_recipe_sha256": inspection[
            "fusion_on_downstream_operation_recipe_sha256"],
        "fusion_off_downstream_operation_recipe_sha256": inspection[
            "fusion_off_downstream_operation_recipe_sha256"],
        "native_library_sha256": _sha(native),
        "native_payload_sha256": _sha(native),
        "target_identity_sha256": inspection["target_identity_sha256"],
        "materializer_source_sha256": _sha(
            source / "scripts/goal5790_home_clean_validate.py"),
        "source_manifest_sha256": _sha(
            source / "history/internal_docs/goal5790_portable_source_manifest.json"),
        "evidence_archive_sha256": _sha(target_evidence),
        "materialization_nonce": "goal5790-home-target-materialization-0001",
        "actual_native_rehashed_from_preserved_payload": True,
        "actual_source_tree_recounted_from_preserved_archive": True,
        "cross_target_native_byte_reproducibility_claimed": False,
    }
    target_authority["receipt_sha256"] = _digest(target_authority)
    authority_path = root / "TARGET_MATERIALIZATION_AUTHORITY.json"
    authority_path.write_text(
        json.dumps(target_authority, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")

    small_edge = root / "small_k4.edge"
    _write_k4(small_edge)
    bounded_root = root / "bounded_inputs"
    bounded_root.mkdir()
    bounded_inputs: dict[str, dict[str, object]] = {}
    for dataset, source_path in real_sources.items():
        view_path = bounded_root / (dataset + "__first262144.edge")
        payload = _write_bounded_prefix(source_path, view_path)
        if hashlib.sha256(payload).hexdigest() != REAL_DATASETS[dataset][
                "prefix_sha256"]:
            raise RuntimeError(f"Goal5790 bounded-view bytes drifted: {dataset}")
        triangle_count = _triangle_count(payload)
        if triangle_count != REAL_DATASETS[dataset]["prefix_triangle_count"]:
            raise RuntimeError(f"Goal5790 bounded-view oracle drifted: {dataset}")
        bounded_inputs[dataset] = {
            "path": view_path,
            "expected_triangle_count": triangle_count,
            "bounded_view_sha256": _sha(view_path),
        }
    raw = root / "functional_raw"
    raw.mkdir()
    lanes = []
    lane_specs: list[tuple[str, str, Path, int, str, str, str, int, str, int]] = []
    small_sha = _sha(small_edge)
    for lifecycle in ("cold", "prepared"):
        lane_specs.append((
            "small", "four_vertex_clique", small_edge, 4,
            "independent_stdlib_simple_undirected_triangle_recount_from_shipped_bounded_edges",
            lifecycle, "inline_fixture", small_edge.stat().st_size,
            "entire_inline_fixture", 6,
        ))
    for dataset, identity in REAL_DATASETS.items():
        bounded = bounded_inputs[dataset]
        lane_specs.append((
            "bounded_real", dataset, bounded["path"],
            int(bounded["expected_triangle_count"]),
            "independent_stdlib_simple_undirected_triangle_recount_from_shipped_bounded_edges",
            "bounded_smoke", "frozen_full_file_prefix",
            int(identity["size_bytes"]), REAL_PREFIX_RULE,
            PREFIX_EDGE_RECORD_COUNT,
        ))
    for (input_kind, dataset, edge, expected, oracle, lifecycle, source_mode,
         original_size, prefix_rule, prefix_count) in lane_specs:
        original_sha = (
            small_sha if input_kind == "small" else REAL_DATASETS[dataset]["sha256"])
        for variant in ("fusion_on", "fusion_off"):
            name = f"{input_kind}__{dataset}__{lifecycle}__{variant}.json"
            output = raw / name
            _run(common + [
                "--mode", "functional",
                "--shared-freeze", str(outer / "SHARED_CONTRACT_FREEZE.json"),
                "--target-materialization", str(authority_path),
                "--input-kind", input_kind, "--dataset", dataset,
                "--edge-file", str(edge),
                "--expected-triangle-count", str(expected),
                "--max-relation-rows", str(args.max_relation_rows),
                "--oracle-authority", oracle,
                "--source-mode", source_mode,
                "--original-edge-filename", (
                    small_edge.name if input_kind == "small"
                    else str(REAL_DATASETS[dataset]["filename"])),
                "--original-edge-sha256", str(original_sha),
                "--original-edge-size-bytes", str(original_size),
                "--prefix-rule", prefix_rule,
                "--prefix-edge-count", str(prefix_count),
                "--variant", variant, "--lifecycle", lifecycle,
                "--output", str(output),
            ], cwd=source, env=env, log=logs / (name + ".log"))
            lane_value = json.loads(output.read_text(encoding="utf-8"))
            if lane_value.get("ptx_program_identity") \
                    != inspection["ptx_program_identity"] \
                    or lane_value.get("ptx_program_identity_sha256") \
                        != ptx_program_identity_sha256:
                raise RuntimeError(
                    "Goal5790 functional lane PTX identity differs from inspection")
            lanes.append(name)
    if len(lanes) != 10:
        raise RuntimeError("Goal5790 functional lane cardinality drift")
    recount_path = root / "FUNCTIONAL_RECOUNT.json"
    _run([
        str(python), str(source / "scripts/goal5790_recount_home_functional.py"),
        "--raw", str(raw), "--expected-native-sha256", _sha(native),
        "--output", str(recount_path),
    ], cwd=source, env=env, log=logs / "functional_recount.log")
    recount = json.loads(recount_path.read_text(encoding="utf-8"))
    if recount.get("exact_lane_count") != 10 \
            or recount.get("behavioral_true_optix_lane_count") != 10 \
            or recount.get("ptx_program_identity_sha256") \
                != ptx_program_identity_sha256:
        raise RuntimeError("Goal5790 independent recount did not close 10/10")

    shutil.copy2(outer / "SOURCE.tar.gz", root / "EXECUTION_SOURCE.tar.gz")
    shutil.copy2(native, root / "librtdl_optix.so")
    result = {
        "schema": "rtdl.goal5790.home_clean_functional_closure.v1",
        "status": "PASS__10_OF_10_EXACT_BEHAVIORAL_EVENT_DERIVED",
        "bundle_sha256": _sha(bundle),
        "executing_harness_sha256": executing_harness_sha,
        "execution_source_archive_sha256": _sha(root / "EXECUTION_SOURCE.tar.gz"),
        "execution_source_tree_sha256": source_manifest["source_tree_sha256"],
        "source_manifest_sha256": _sha(
            source / "history/internal_docs/goal5790_portable_source_manifest.json"),
        "native_library_sha256": _sha(root / "librtdl_optix.so"),
        "target_materialization_evidence_sha256": _sha(target_evidence),
        "target_materialization_receipt_sha256": target_authority["receipt_sha256"],
        "shared_contract_freeze_file_sha256": _sha(
            outer / "SHARED_CONTRACT_FREEZE.json"),
        "expected_value_and_fallback_sha256": _sha(
            outer / "EXPECTED_VALUE_AND_FALLBACK.json"),
        "home_machine_authority_file_sha256": _sha(
            outer / "HOME_MACHINE_AUTHORITY.json"),
        "home_machine_authority_sha256": home_machine_authority[
            "receipt_sha256"],
        "home_machine_authority": home_machine_authority,
        "ptx_producer_toolchain_files": ptx_toolchain_files,
        "ptx_producer_observation": versions,
        "ptx_producer_open_audit": producer_open_audit,
        "ptx_program_identity_sha256": ptx_program_identity_sha256,
        "target_program_inspection_sha256": _sha(inspect_path),
        "cupy_nvrtc_runtime_version": versions[
            "cupy_nvrtc_runtime_version"],
        "loaded_nvrtc_family_paths": versions["loaded_nvrtc_family_paths"],
        "gpu": gpu,
        "versions": versions,
        "focused_tests_passed": "OK" in test_output,
        "home_functional_lane_count": 10,
        "bounded_real_dataset_count": 3,
        "bounded_prefix_edge_record_count": PREFIX_EDGE_RECORD_COUNT,
        "bounded_input_manifest": {
            dataset: {
                "original_full_edge_sha256": REAL_DATASETS[dataset]["sha256"],
                "original_full_edge_filename": REAL_DATASETS[dataset]["filename"],
                "original_full_edge_size_bytes": REAL_DATASETS[dataset]["size_bytes"],
                "bounded_view_edge_sha256": bounded_inputs[dataset][
                    "bounded_view_sha256"],
                "expected_triangle_count": bounded_inputs[dataset][
                    "expected_triangle_count"],
            }
            for dataset in sorted(REAL_DATASETS)
        },
        "exact_lane_count": recount["exact_lane_count"],
        "behavioral_true_optix_lane_count": recount[
            "behavioral_true_optix_lane_count"],
        "fresh_parent_pid_count": recount["fresh_parent_pid_count"],
        "traversal_receipt_count": recount["traversal_receipt_count"],
        "operation_receipt_count": recount["operation_receipt_count"],
        "successful_operation_event_count": recount[
            "successful_operation_event_count"],
        "operation_receipt_count_by_variant": recount[
            "operation_receipt_count_by_variant"],
        "successful_operation_event_count_by_variant": recount[
            "successful_operation_event_count_by_variant"],
        "invalid_traversal_or_operation_receipt_count": recount[
            "invalid_traversal_or_operation_receipt_count"],
        "particle_included": False,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "exact_source_and_native_preserved_before_first_functional_lane": True,
        "performance_or_compiler_fusion_claimed": False,
        "home_timing_is_diagnostic_only": True,
        "execution_environment_class": home_machine_authority[
            "execution_environment_class"],
        "pod_used": home_machine_authority["pod_used"],
        "private_codex_dependency_used": False,
        "prebuilt_target_native_used": False,
        "runtime_platform": platform.platform(),
    }
    (root / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
