from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Sequence
import uuid

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from author_source_policy import (
    PINNED_AUTHOR_COMMIT,
    PINNED_AUTHOR_REMOTE,
    validate_author_source_identity,
)


QUERY_IDS = (
    "q11",
    "q12",
    "q13",
    "q21",
    "q22",
    "q23",
    "q31",
    "q32",
    "q33",
    "q34",
    "q41",
    "q42",
    "q43",
)
AUTHOR_COMMIT = PINNED_AUTHOR_COMMIT
AUTHOR_REMOTE = PINNED_AUTHOR_REMOTE
AUTHOR_COMPATIBILITY_PATCH = "author_patches/Makefile.gcc-current.patch"
INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
GENERATION_PROFILE = (
    "ssb_dbgen_default_customer_supplier_then_individual_part_date_lineorder_v1"
)
EXECUTION_IDENTITY_SCHEMA = "rtdl.paper_reproduction.execution_cohort.v2"


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _gpu_identity() -> str:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=uuid,name,pci.bus_id",
            "--format=csv,noheader,nounits",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or not value:
        raise RuntimeError("cannot establish the GPU identity for the evidence cohort")
    return value


def _author_source_identity(binary: Path) -> dict[str, object]:
    resolved = binary.resolve()
    repository = next(
        (parent for parent in resolved.parents if (parent / ".git").exists()),
        None,
    )
    if repository is None:
        raise RuntimeError("author binary is not inside a Git checkout")

    def git(*arguments: str) -> bytes:
        return subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=True,
            capture_output=True,
        ).stdout

    return {
        "repository_path": str(repository),
        "repository_remote": git("config", "--get", "remote.origin.url")
        .decode("utf-8", errors="replace")
        .strip(),
        "commit": git("rev-parse", "HEAD").decode("ascii").strip(),
        "status_porcelain": git(
            "status", "--porcelain=v1", "--untracked-files=all"
        )
        .decode("utf-8", errors="replace")
        .splitlines(),
        "tracked_diff_sha256": hashlib.sha256(
            git("diff", "--binary", "HEAD")
        ).hexdigest(),
        "identity_complete": True,
    }


def _identity_mismatches(
    current: dict[str, object], existing: dict[str, object]
) -> dict[str, dict[str, object]]:
    return {
        key: {"expected": value, "observed": existing.get(key)}
        for key, value in current.items()
        if existing.get(key) != value
    }


def _prepare_execution_identity(args: argparse.Namespace) -> dict[str, object]:
    native_library = Path(os.environ.get("RTDL_OPTIX_LIB", ""))
    if not native_library.is_file():
        raise RuntimeError("RTDL_OPTIX_LIB must name the exact native library under test")
    source_identity = _author_source_identity(args.author_binary)
    patch_path = args.app_root / AUTHOR_COMPATIBILITY_PATCH
    validate_author_source_identity(
        source_identity,
        compatibility_patch_path=patch_path,
    )
    current = {
        "schema": EXECUTION_IDENTITY_SCHEMA,
        "host": socket.gethostname(),
        "gpu_identity": _gpu_identity(),
        "matrix_runner_sha256": _sha256_file(Path(__file__)),
        "author_runner_sha256": _sha256_file(args.app_root / "raydb_reproduction.py"),
        "rtdl_runner_sha256": _sha256_file(args.app_root / "run_ssb_packet_rtdl.py"),
        "generic_primitives_sha256": _sha256_file(
            args.project_root / "src" / "rtdsl" / "generic_primitives.py"
        ),
        "optix_runtime_sha256": _sha256_file(
            args.project_root / "src" / "rtdsl" / "optix_runtime.py"
        ),
        "native_library_sha256": _sha256_file(native_library),
        "author_binary_sha256": _sha256_file(args.author_binary),
        "author_repository_path": source_identity["repository_path"],
        "author_repository_remote": source_identity["repository_remote"],
        "author_commit": source_identity["commit"],
        "author_status_porcelain": source_identity["status_porcelain"],
        "author_tracked_diff_sha256": source_identity["tracked_diff_sha256"],
        "author_compatibility_patch_sha256": _sha256_file(patch_path),
    }
    identity_path = args.evidence_root / "matrix_execution_identity.json"
    if identity_path.is_file():
        existing = _load_json(identity_path)
        mismatches = _identity_mismatches(current, existing)
        if mismatches:
            raise RuntimeError(
                "existing evidence belongs to a different code/host/GPU identity: "
                + json.dumps(mismatches, sort_keys=True)
            )
        cohort_id = existing.get("evidence_cohort_id")
        if not isinstance(cohort_id, str) or not cohort_id:
            raise RuntimeError("existing execution identity lacks an evidence cohort id")
    else:
        cohort_id = uuid.uuid4().hex
    identity = {**current, "evidence_cohort_id": cohort_id}
    _write_json_atomic(identity_path, identity)
    return identity


def _partition_ledger_verified(
    rtdl: dict[str, object],
    *,
    row_count: int,
    expected_partition_rows: int,
) -> bool:
    ledger = rtdl.get("partition_ledger")
    if not isinstance(ledger, list) or not ledger:
        return False
    cursor = 0
    allowed_symbols = {
        "rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_signed_v2",
        "rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_with_phase_timings_signed_v2",
    }
    if rtdl.get("partition_ledger_schema") != "rtdl.generic.partition_ledger.v2":
        return False
    for index, entry in enumerate(ledger):
        if not isinstance(entry, dict):
            return False
        start = int(entry.get("primitive_id_start", -1))
        stop = int(entry.get("primitive_id_stop", -1))
        count = int(entry.get("primitive_count", -1))
        phase = entry.get("phase_timing_seconds")
        if not (
            int(entry.get("partition_index", -1)) == index
            and start == cursor
            and stop - start == count
            and 0 < count <= expected_partition_rows
            and entry.get("backend") == "optix"
            and entry.get("native_symbol") in allowed_symbols
            and entry.get("launch_completed") is True
            and int(entry.get("result_row_count", -1)) >= 0
            and len(str(entry.get("result_rows_checksum_fnv1a64", ""))) == 16
            and entry.get("checksum_schema") == "fnv1a64_standard_offset_basis.v2"
            and isinstance(entry.get("partition_call_wall_sec"), (int, float))
            and float(entry["partition_call_wall_sec"]) >= 0.0
            and isinstance(entry.get("host_merge_wall_sec"), (int, float))
            and float(entry["host_merge_wall_sec"]) >= 0.0
            and int(entry.get("hit_event_count_before_dedup", -1)) >= 0
            and isinstance(phase, dict)
            and isinstance(phase.get("launch"), (int, float))
            and float(phase["launch"]) >= 0.0
        ):
            return False
        cursor = stop
    return cursor == row_count


def _run(command: list[str], *, env: dict[str, str]) -> dict[str, object]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    elapsed = time.perf_counter() - started
    result = {
        "command": command,
        "returncode": int(completed.returncode),
        "elapsed_seconds": elapsed,
    }
    if completed.returncode != 0:
        result["stdout_tail"] = completed.stdout[-4000:]
        result["stderr_tail"] = completed.stderr[-4000:]
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def _existing_case(
    build_path: Path,
    author_path: Path,
    rtdl_path: Path,
    *,
    partition_rows: int,
    dataset_provenance: dict[str, object],
    packet_path: Path,
    matrix_runner_sha256: str,
    execution_identity: dict[str, object],
) -> dict[str, object] | None:
    if not all(path.is_file() for path in (build_path, author_path, rtdl_path)):
        return None
    build = _load_json(build_path)
    author = _load_json(author_path)
    rtdl = _load_json(rtdl_path)
    if (
        author.get("schema") != "rtdl.paper_reproduction.raydb.author_packet_gate.v2"
        or rtdl.get("schema") != "rtdl.paper_reproduction.raydb.ssb_packet_rtdl_gate.v3"
    ):
        return None
    return _case_summary(
        build,
        author,
        rtdl,
        commands=[],
        resumed=True,
        expected_partition_rows=partition_rows,
        dataset_provenance=dataset_provenance,
        build_path=build_path,
        author_path=author_path,
        rtdl_path=rtdl_path,
        packet_path=packet_path,
        matrix_runner_sha256=matrix_runner_sha256,
        execution_identity=execution_identity,
    )


def _strict_json_int(value: object, *, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact JSON integer")
    if value < INT64_MIN or value > INT64_MAX:
        raise OverflowError(f"{label} is outside signed int64")
    return value


def _canonical_rows(
    payload: dict[str, object],
    key: str,
    *,
    expected_group_arity: int,
) -> list[tuple[tuple[int, ...], int]]:
    raw_rows = payload.get(key)
    if not isinstance(raw_rows, list):
        raise TypeError(f"{key} must be a JSON row list")
    rows: list[tuple[tuple[int, ...], int]] = []
    groups: set[tuple[int, ...]] = set()
    for index, row in enumerate(raw_rows):
        if not isinstance(row, dict) or not isinstance(row.get("group"), list):
            raise TypeError(f"{key}[{index}] must contain a group list")
        if len(row["group"]) != expected_group_arity:
            raise ValueError(f"{key}[{index}] group arity mismatch")
        group = tuple(
            _strict_json_int(value, label=f"{key}[{index}].group")
            for value in row["group"]
        )
        if group in groups:
            raise ValueError(f"{key} contains duplicate group {group!r}")
        groups.add(group)
        rows.append(
            (group, _strict_json_int(row.get("value"), label=f"{key}[{index}].value"))
        )
    return sorted(rows)


def _case_summary(
    build: dict[str, object],
    author: dict[str, object],
    rtdl: dict[str, object],
    *,
    commands: list[dict[str, object]],
    resumed: bool,
    expected_partition_rows: int,
    dataset_provenance: dict[str, object],
    build_path: Path,
    author_path: Path,
    rtdl_path: Path,
    packet_path: Path,
    matrix_runner_sha256: str,
    execution_identity: dict[str, object],
) -> dict[str, object]:
    packet = build["packet"]
    group_arity = _strict_json_int(
        packet.get("group_dimension_count"), label="packet.group_dimension_count"
    )
    if group_arity < 0:
        raise ValueError("packet.group_dimension_count must be nonnegative")
    expected_rows = _canonical_rows(
        packet, "expected_rows", expected_group_arity=group_arity
    )
    author_rows = _canonical_rows(
        author, "author_rows", expected_group_arity=group_arity
    )
    rtdl_rows = _canonical_rows(rtdl, "rtdl_rows", expected_group_arity=group_arity)
    complete_rows_equal = expected_rows == author_rows == rtdl_rows
    expected_hashes = {
        "data_sha256": str(packet["data_sha256"]),
        "predicate_sha256": str(packet["predicate_sha256"]),
        "expected_rows_sha256": str(packet["expected_rows_sha256"]),
    }
    packet_json_sha256 = _sha256_file(packet_path)
    author_result_sha256 = _sha256_file(author_path)
    build_result_sha256 = _sha256_file(build_path)
    rtdl_result_sha256 = _sha256_file(rtdl_path)
    observed_packet_hashes = dict(expected_hashes)
    evidence_schema_verified = bool(
        build.get("schema")
        == "rtdl.paper_reproduction.raydb.ssb_single_query_packet_build.v1"
        and packet.get("schema") == "rtdl.paper_reproduction.raydb.ssb_packet.v2"
        and author.get("schema")
        == "rtdl.paper_reproduction.raydb.author_packet_gate.v2"
        and author.get("packet_schema") == packet.get("schema")
        and rtdl.get("schema")
        == "rtdl.paper_reproduction.raydb.ssb_packet_rtdl_gate.v3"
        and rtdl.get("packet_schema") == packet.get("schema")
    )
    expected_child_identity = {
        "evidence_cohort_id": execution_identity["evidence_cohort_id"],
        "host": execution_identity["host"],
        "gpu_identity": execution_identity["gpu_identity"],
        "matrix_runner_sha256": execution_identity["matrix_runner_sha256"],
    }
    expected_author_source_identity = {
        "repository_path": execution_identity["author_repository_path"],
        "repository_remote": execution_identity["author_repository_remote"],
        "commit": execution_identity["author_commit"],
        "status_porcelain": execution_identity["author_status_porcelain"],
        "tracked_diff_sha256": execution_identity["author_tracked_diff_sha256"],
        "identity_complete": True,
    }
    author_execution_identity_verified = bool(
        author.get("packet_json_sha256") == packet_json_sha256
        and author.get("packet_file_hashes_before") == observed_packet_hashes
        and author.get("packet_file_hashes_after") == observed_packet_hashes
        and author.get("packet_files_stable_during_author_run") is True
        and author.get("author_binary_sha256")
        == execution_identity["author_binary_sha256"]
        and author.get("runner_sha256") == execution_identity["author_runner_sha256"]
        and author.get("execution_identity") == expected_child_identity
        and author.get("author_source_identity") == expected_author_source_identity
    )
    rtdl_execution_identity_verified = bool(
        rtdl.get("packet_json_sha256") == packet_json_sha256
        and rtdl.get("author_result_sha256") == author_result_sha256
        and rtdl.get("author_evidence_verified") is True
        and rtdl.get("same_packet_bytes_as_author") is True
        and rtdl.get("native_library_sha256")
        == execution_identity["native_library_sha256"]
        and rtdl.get("runner_sha256") == execution_identity["rtdl_runner_sha256"]
        and rtdl.get("generic_primitives_sha256")
        == execution_identity["generic_primitives_sha256"]
        and rtdl.get("optix_runtime_sha256")
        == execution_identity["optix_runtime_sha256"]
        and rtdl.get("execution_identity") == expected_child_identity
    )
    same_execution_cohort_verified = bool(
        matrix_runner_sha256 == execution_identity["matrix_runner_sha256"]
        and author.get("execution_identity") == rtdl.get("execution_identity")
        and author.get("execution_identity") == expected_child_identity
    )
    same_packet_hashes = all(
        str(author.get(name, "")) == value and str(rtdl.get(name, "")) == value
        for name, value in expected_hashes.items()
    )
    same_case_identity = bool(
        str(author.get("query_id", "")) == str(build["query_id"])
        and str(rtdl.get("query_id", "")) == str(build["query_id"])
        and int(author.get("scale_factor", -1)) == int(build["scale_factor"])
        and int(rtdl.get("scale_factor", -1)) == int(build["scale_factor"])
        and int(author.get("row_count", -1)) == int(build["row_count"])
        and int(rtdl.get("row_count", -1)) == int(build["row_count"])
    )
    provenance_tables = dataset_provenance.get("tables", {})
    provenance_table_hashes = {
        name: str(entry.get("sha256", ""))
        for name, entry in provenance_tables.items()
        if isinstance(entry, dict)
    } if isinstance(provenance_tables, dict) else {}
    expected_dimension_counts = {
        "customer": 30_000 * int(build["scale_factor"]),
        "supplier": 2_000 * int(build["scale_factor"]),
        "part": 200_000 * math.floor(1.0 + math.log2(float(build["scale_factor"]))),
    }
    provenance_row_counts = {
        name: int(entry.get("row_count", -1))
        for name, entry in provenance_tables.items()
        if isinstance(entry, dict)
    } if isinstance(provenance_tables, dict) else {}
    dataset_provenance_verified = bool(
        dataset_provenance.get("schema")
        == "rtdl.paper_reproduction.raydb.ssb_generated_dataset_provenance.v1"
        and dataset_provenance.get("dbgen_commit") == build.get("dbgen_commit")
        and dataset_provenance.get("dataset_identity_level")
        == "deterministic_generated_same_source_not_exact_paper_input"
        and dataset_provenance.get("generation_profile") == GENERATION_PROFILE
        and isinstance(dataset_provenance.get("generation_commands"), list)
        and bool(dataset_provenance.get("generation_commands"))
        and isinstance(dataset_provenance.get("generation_command_argv"), list)
        and bool(dataset_provenance.get("generation_command_argv"))
        and dataset_provenance.get("dbgen_checkout_clean") is True
        and all(
            isinstance(dataset_provenance.get(field), str)
            and len(str(dataset_provenance.get(field))) == 64
            for field in (
                "dbgen_tracked_source_tree_sha256",
                "dbgen_binary_sha256",
                "dists_dss_sha256",
            )
        )
        and int(dataset_provenance.get("dbgen_tracked_source_tree_file_count", 0)) > 0
        and dataset_provenance.get("provenance_scope")
        == "bounded_same_source_only_not_exact_paper"
        and isinstance(dataset_provenance.get("claim_boundary"), dict)
        and dataset_provenance["claim_boundary"].get("bounded_same_source_only") is True
        and dataset_provenance["claim_boundary"].get("exact_paper_input_claimed") is False
        and dataset_provenance["claim_boundary"].get("exact_paper_dataset_claimed") is False
        and int(dataset_provenance.get("scale_factor", -1)) == int(build["scale_factor"])
        and int(dataset_provenance.get("lineorder_row_count", -1)) == int(build["row_count"])
        and all(provenance_row_counts.get(name) == expected for name, expected in expected_dimension_counts.items())
        and 5_500_000 * int(build["scale_factor"])
        <= int(build["row_count"])
        <= 6_500_000 * int(build["scale_factor"])
        and provenance_table_hashes == {
            name: str(value) for name, value in dict(build.get("table_sha256", {})).items()
        }
    )
    expected_partition_count = (
        int(build["row_count"]) + int(expected_partition_rows) - 1
    ) // int(expected_partition_rows)
    partition_contract = rtdl.get("partition_execution_contract")
    primitive_value_derivation = rtdl.get("primitive_value_derivation")
    primitive_value_derivation_verified = bool(
        isinstance(primitive_value_derivation, dict)
        and primitive_value_derivation.get("contract")
        == "signed_i32_product_exact_in_signed_i64.v1"
        and primitive_value_derivation.get("source_dtype") == "int32"
        and primitive_value_derivation.get("overflow_fail_closed_before_multiplication")
        is True
        and primitive_value_derivation.get("complex_aggregate")
        is bool(packet.get("complex_aggregate"))
    )
    partition_evidence_verified = bool(
        rtdl.get("backend") == "optix"
        and
        rtdl.get("partitioned_execution_requested") is True
        and int(rtdl.get("expected_primitive_count", -1)) == int(build["row_count"])
        and int(rtdl.get("partition_rows", -1)) == int(expected_partition_rows)
        and int(rtdl.get("partition_count", -1)) == expected_partition_count
        and 0 < int(rtdl.get("peak_partition_primitive_count", 0)) <= int(expected_partition_rows)
        and (
            expected_partition_count <= 1
            or rtdl.get("prepared_ray_batch_reused_across_partitions") is True
        )
        and isinstance(partition_contract, dict)
        and partition_contract.get("contract")
        == "GENERIC_PARTITIONED_RAY_TRIANGLE_GROUPED_I64_REDUCTION_3D_V2"
        and partition_contract.get("app_semantics") == "none"
        and int(rtdl.get("triangle_count", -1)) == int(build["row_count"])
        and _partition_ledger_verified(
            rtdl,
            row_count=int(build["row_count"]),
            expected_partition_rows=int(expected_partition_rows),
        )
    )
    timing_denominators = rtdl.get("timing_denominators")
    timing_evidence_verified = bool(
        isinstance(timing_denominators, dict)
        and timing_denominators.get("route_total_includes_partition_triangle_pack") is True
        and timing_denominators.get("partition_triangle_pack_is_nested_not_additive") is True
        and isinstance(timing_denominators.get("nesting_graph"), dict)
        and timing_denominators["nesting_graph"].get("schema")
        == "rtdl.timing.nesting_graph.v1"
        and isinstance(rtdl.get("phase_timing_contract"), dict)
        and rtdl["phase_timing_contract"].get("schema")
        == "rtdl.generic.partitioned_grouped_i64.phase_timing.v2"
    )
    evidence_bundle = {
        "schema": "rtdl.paper_reproduction.raydb.scale_case_evidence_bundle.v2",
        "dataset_manifest_sha256": str(dataset_provenance.get("manifest_sha256", "")),
        "packet_json_sha256": packet_json_sha256,
        **expected_hashes,
        "build_result_sha256": build_result_sha256,
        "author_result_sha256": author_result_sha256,
        "rtdl_result_sha256": rtdl_result_sha256,
        "author_binary_sha256": str(author.get("author_binary_sha256", "")),
        "author_source_identity": author.get("author_source_identity"),
        "author_runner_sha256": str(author.get("runner_sha256", "")),
        "rtdl_native_library_sha256": str(rtdl.get("native_library_sha256", "")),
        "rtdl_runner_sha256": str(rtdl.get("runner_sha256", "")),
        "matrix_runner_sha256": matrix_runner_sha256,
        "execution_identity": execution_identity,
        "partition_rows": int(expected_partition_rows),
    }
    return {
        "query_id": str(build["query_id"]),
        "scale_factor": int(build["scale_factor"]),
        "row_count": int(build["row_count"]),
        **expected_hashes,
        "same_packet_hashes": same_packet_hashes,
        "same_case_identity": same_case_identity,
        "dataset_provenance_verified": dataset_provenance_verified,
        "dataset_provenance_sha256": str(dataset_provenance.get("manifest_sha256", "")),
        "partition_evidence_verified": partition_evidence_verified,
        "primitive_value_derivation_verified": primitive_value_derivation_verified,
        "evidence_schema_verified": evidence_schema_verified,
        "author_execution_identity_verified": author_execution_identity_verified,
        "rtdl_execution_identity_verified": rtdl_execution_identity_verified,
        "same_execution_cohort_verified": same_execution_cohort_verified,
        "timing_evidence_verified": timing_evidence_verified,
        "evidence_bundle": evidence_bundle,
        "expected_partition_count": expected_partition_count,
        "expected_group_count": len(expected_rows),
        "author_group_count": len(author_rows),
        "rtdl_group_count": len(rtdl_rows),
        "author_matches_oracle": bool(author.get("author_matches_cpu_oracle", False)),
        "rtdl_matches_oracle": bool(rtdl.get("rtdl_matches_oracle", False)),
        "complete_grouped_rows_equal": complete_rows_equal,
        "partition_count": int(rtdl.get("partition_count", 1)),
        "peak_live_primitive_rows": int(
            rtdl.get("peak_partition_primitive_count", rtdl.get("row_count", 0))
        ),
        "prepared_ray_batch_reused_across_partitions": bool(
            rtdl.get("prepared_ray_batch_reused_across_partitions", False)
        ),
        "phase_timing_seconds": rtdl.get("phase_timing_seconds", {}),
        "timing_denominators": timing_denominators,
        "partition_ledger": rtdl.get("partition_ledger", []),
        "commands": commands,
        "resumed_from_existing_evidence": resumed,
        "passed": bool(
            author.get("author_matches_cpu_oracle", False)
            and rtdl.get("rtdl_matches_oracle", False)
            and same_packet_hashes
            and same_case_identity
            and evidence_schema_verified
            and author_execution_identity_verified
            and rtdl_execution_identity_verified
            and same_execution_cohort_verified
            and dataset_provenance_verified
            and partition_evidence_verified
            and primitive_value_derivation_verified
            and timing_evidence_verified
            and complete_rows_equal
        ),
    }


def run_case(args: argparse.Namespace, query_id: str, env: dict[str, str]) -> dict[str, object]:
    packet_dir = args.packet_root / query_id
    build_path = args.evidence_root / f"goal5562_sf{args.scale_factor}_{query_id}_packet_build.json"
    author_path = args.evidence_root / f"goal5562_sf{args.scale_factor}_{query_id}_author.json"
    rtdl_path = args.evidence_root / f"goal5562_sf{args.scale_factor}_{query_id}_rtdl_partitioned.json"

    if args.resume and not args.rerun_rtdl:
        existing = _existing_case(
            build_path,
            author_path,
            rtdl_path,
            partition_rows=args.partition_rows,
            dataset_provenance=args.dataset_provenance,
            packet_path=packet_dir / "packet.json",
            matrix_runner_sha256=args.matrix_runner_sha256,
            execution_identity=args.execution_identity,
        )
        if existing is not None and existing["passed"]:
            return existing

    commands: list[dict[str, object]] = []
    reuse_build_and_author = bool(
        args.rerun_rtdl and build_path.is_file() and author_path.is_file()
    )
    reuse_build_only = bool(
        args.rerun_author_and_rtdl and build_path.is_file()
    )
    build_command = [
        sys.executable,
        str(args.app_root / "build_ssb_sf1_matrix.py"),
        "--dataset-dir",
        str(args.dataset_dir),
        "--output-root",
        str(args.packet_root),
        "--output-json",
        str(build_path),
        "--query-id",
        query_id,
        "--scale-factor",
        str(args.scale_factor),
        "--dataset-provenance-json",
        str(args.dataset_provenance_json),
    ]
    if args.memory_limit:
        build_command.extend(("--memory-limit", args.memory_limit))
    if args.temp_directory:
        build_command.extend(("--temp-directory", str(args.temp_directory)))
    if not reuse_build_and_author and not reuse_build_only:
        commands.append(_run(build_command, env=env))

    author_command = [
        sys.executable,
        str(args.app_root / "raydb_reproduction.py"),
        "run-author-packet",
        "--author-binary",
        str(args.author_binary),
        "--packet-json",
        str(packet_dir / "packet.json"),
        "--output-json",
        str(author_path),
    ]
    if not reuse_build_and_author:
        commands.append(_run(author_command, env=env))

    rtdl_command = [
        sys.executable,
        str(args.app_root / "run_ssb_packet_rtdl.py"),
        "--packet-json",
        str(packet_dir / "packet.json"),
        "--author-result",
        str(author_path),
        "--output-json",
        str(rtdl_path),
        "--partition-rows",
        str(args.partition_rows),
    ]
    commands.append(_run(rtdl_command, env=env))

    return _case_summary(
        _load_json(build_path),
        _load_json(author_path),
        _load_json(rtdl_path),
        commands=commands,
        resumed=False,
        expected_partition_rows=args.partition_rows,
        dataset_provenance=args.dataset_provenance,
        build_path=build_path,
        author_path=author_path,
        rtdl_path=rtdl_path,
        packet_path=packet_dir / "packet.json",
        matrix_runner_sha256=args.matrix_runner_sha256,
        execution_identity=args.execution_identity,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a resumable generated-SSB author/RTDL partitioned correctness matrix"
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--packet-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--author-binary", type=Path, required=True)
    parser.add_argument("--scale-factor", type=int, required=True)
    parser.add_argument("--partition-rows", type=int, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--dataset-provenance-json", type=Path, required=True)
    parser.add_argument("--memory-limit")
    parser.add_argument("--temp-directory", type=Path)
    parser.add_argument("--query-id", action="append", choices=QUERY_IDS)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--rerun-rtdl",
        action="store_true",
        help="Reuse existing packet/author evidence but recompute every RTDL case",
    )
    parser.add_argument(
        "--rerun-author-and-rtdl",
        action="store_true",
        help="Reuse an existing packet build, then recompute author and RTDL evidence",
    )
    args = parser.parse_args(argv)
    if args.scale_factor <= 0 or args.partition_rows <= 0:
        parser.error("scale factor and partition rows must be positive")
    args.app_root = args.project_root / "Paper-reproduction-apps" / "raydb-paper"
    args.packet_root.mkdir(parents=True, exist_ok=True)
    args.evidence_root.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.dataset_provenance = _load_json(args.dataset_provenance_json)
    args.dataset_provenance["manifest_sha256"] = hashlib.sha256(
        args.dataset_provenance_json.read_bytes()
    ).hexdigest()
    args.matrix_runner_sha256 = _sha256_file(Path(__file__))
    args.execution_identity = _prepare_execution_identity(args)

    env = dict(os.environ)
    source_path = str(args.project_root / "src")
    env["PYTHONPATH"] = source_path + os.pathsep + env.get("PYTHONPATH", "")
    env["RTDL_EVIDENCE_COHORT_ID"] = str(
        args.execution_identity["evidence_cohort_id"]
    )
    env["RTDL_EVIDENCE_GPU_IDENTITY"] = str(args.execution_identity["gpu_identity"])
    env["RTDL_EVIDENCE_MATRIX_RUNNER_SHA256"] = str(
        args.execution_identity["matrix_runner_sha256"]
    )
    query_ids = tuple(args.query_id or QUERY_IDS)
    cases: list[dict[str, object]] = []
    for query_id in query_ids:
        case = run_case(args, query_id, env)
        cases.append(case)
        partial = {
            "schema": "rtdl.paper_reproduction.raydb.generated_ssb_partitioned_matrix.v3",
            "matrix_runner_sha256": args.matrix_runner_sha256,
            "execution_identity": args.execution_identity,
            "scale_factor": args.scale_factor,
            "partition_rows": args.partition_rows,
            "dataset_provenance_json": str(args.dataset_provenance_json),
            "dataset_provenance_sha256": args.dataset_provenance["manifest_sha256"],
            "requested_query_ids": list(query_ids),
            "completed_query_ids": [row["query_id"] for row in cases],
            "cases": cases,
            "all_requested_queries_passed": len(cases) == len(query_ids)
            and all(row["passed"] for row in cases),
            "claim_boundary": {
                "generated_same_source_correctness_claimed": all(row["passed"] for row in cases),
                "all_13_queries_at_scale_claimed": set(query_ids) == set(QUERY_IDS)
                and len(cases) == len(QUERY_IDS)
                and all(row["passed"] for row in cases),
                "exact_paper_input_claimed": False,
                "figure12_reproduced": False,
                "paper_performance_claimed": False,
                "author_rtdl_performance_ratio_authorized": False,
                "author_algorithm_equivalence_claimed": False,
            },
        }
        _write_json_atomic(args.output_json, partial)
        print(json.dumps({"query_id": query_id, "passed": case["passed"]}), flush=True)
    return 0 if all(row["passed"] for row in cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
