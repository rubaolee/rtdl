from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
from typing import Iterable, Sequence


@dataclass(frozen=True)
class FlatRow:
    aggregate_value: int
    group_values: tuple[int, ...]
    scan_values: tuple[int, ...]


@dataclass(frozen=True)
class ExactListPredicate:
    accepted_values: tuple[tuple[int, ...], ...]

    def accepts(self, scan_values: Sequence[int]) -> bool:
        if len(scan_values) != len(self.accepted_values):
            raise ValueError("scan row and predicate dimensions differ")
        return all(
            int(value) in accepted
            for value, accepted in zip(scan_values, self.accepted_values)
        )


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _observed_gpu_identity() -> str | None:
    expected = os.environ.get("RTDL_EVIDENCE_GPU_IDENTITY")
    if expected is None:
        return None
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
    observed = completed.stdout.strip()
    if completed.returncode != 0 or not observed:
        raise RuntimeError("author runner could not observe the cohort GPU identity")
    if observed != expected:
        raise RuntimeError(
            f"author runner GPU identity mismatch: expected {expected!r}, got {observed!r}"
        )
    return observed


def _packet_file_hashes(packet: dict[str, object]) -> dict[str, str]:
    paths = {
        "data_sha256": Path(str(packet["data_path"])),
        "predicate_sha256": Path(str(packet["predicate_path"])),
        "expected_rows_sha256": Path(str(packet["expected_rows_path"])),
    }
    observed = {name: sha256_file(path) for name, path in paths.items()}
    for name, digest in observed.items():
        if digest != str(packet.get(name, "")):
            raise ValueError(
                f"packet {name} does not match the file passed to the author: "
                f"declared={packet.get(name)!r}, observed={digest}"
            )
    return observed


def _author_source_identity(binary: Path) -> dict[str, object]:
    resolved = binary.resolve()
    repository = next(
        (parent for parent in resolved.parents if (parent / ".git").exists()),
        None,
    )
    if repository is None:
        raise ValueError("author binary is not inside a Git checkout")

    def git(*args: str) -> bytes:
        return subprocess.run(
            ["git", "-C", str(repository), *args],
            check=True,
            capture_output=True,
        ).stdout

    commit = git("rev-parse", "HEAD").decode("ascii").strip()
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    diff = git("diff", "--binary", "HEAD")
    remote = git("config", "--get", "remote.origin.url").decode(
        "utf-8", errors="replace"
    ).strip()
    return {
        "repository_path": str(repository),
        "repository_remote": remote,
        "commit": commit,
        "status_porcelain": status.decode("utf-8", errors="replace").splitlines(),
        "tracked_diff_sha256": hashlib.sha256(diff).hexdigest(),
        "identity_complete": True,
    }


def bounded_q21_rows() -> tuple[FlatRow, ...]:
    return (
        FlatRow(10, (1992, 12), (12, 1)),
        FlatRow(20, (1992, 12), (12, 1)),
        FlatRow(7, (1992, 13), (13, 1)),
        FlatRow(5, (1993, 12), (12, 1)),
        FlatRow(11, (1993, 12), (12, 0)),
        FlatRow(13, (1994, 12), (12, 1)),
        FlatRow(17, (1992, 12), (12, 1)),
        FlatRow(19, (1994, 14), (14, 1)),
        FlatRow(23, (1995, 12), (12, 4)),
        FlatRow(29, (1995, 15), (15, 3)),
    )


def bounded_q21_predicate() -> ExactListPredicate:
    return ExactListPredicate(((12,), (1,)))


def canonical_grouped_sum_rows(
    rows: Iterable[FlatRow], predicate: ExactListPredicate
) -> list[dict[str, object]]:
    grouped: dict[tuple[int, ...], int] = {}
    for row in rows:
        if predicate.accepts(row.scan_values):
            grouped[row.group_values] = (
                grouped.get(row.group_values, 0) + int(row.aggregate_value)
            )
    return [
        {"group": list(group), "value": value}
        for group, value in sorted(grouped.items())
        if value != 0
    ]


def lower_rows_to_generic_rt(
    rows: Sequence[FlatRow], predicate: ExactListPredicate
) -> dict[str, object]:
    import rtdsl as rt

    rows = tuple(rows)
    if not rows:
        raise ValueError("at least one RayDB row is required")
    group_dims = len(rows[0].group_values)
    scan_dims = len(rows[0].scan_values)
    if group_dims < 1 or scan_dims < 1:
        raise ValueError("RayDB group and scan dimensions must be nonempty")
    if len(predicate.accepted_values) != scan_dims:
        raise ValueError("RayDB predicate dimensions must match scan dimensions")
    for row in rows:
        if len(row.group_values) != group_dims or len(row.scan_values) != scan_dims:
            raise ValueError("all RayDB rows must share one fixed column schema")
    group_tuples = sorted({row.group_values for row in rows})
    group_to_id = {group: index for index, group in enumerate(group_tuples)}
    scan_value_maps = [
        {value: index for index, value in enumerate(sorted({row.scan_values[dim] for row in rows}))}
        for dim in range(len(rows[0].scan_values))
    ]
    scan_radices = [len(mapping) for mapping in scan_value_maps]

    def encode_scan(values: Sequence[int]) -> int:
        encoded = 0
        rate = 1
        for dim in range(len(values) - 1, -1, -1):
            encoded += scan_value_maps[dim][int(values[dim])] * rate
            rate *= scan_radices[dim]
        return encoded

    triangles = tuple(
        rt.Triangle3D(
            id=index,
            x0=float(row.aggregate_value),
            y0=float(group_to_id[row.group_values]),
            z0=float(encode_scan(row.scan_values)),
            x1=float(row.aggregate_value + 4000),
            y1=float(group_to_id[row.group_values]),
            z1=float(encode_scan(row.scan_values)),
            x2=float(row.aggregate_value),
            y2=float(group_to_id[row.group_values] + 28),
            z2=float(encode_scan(row.scan_values)),
        )
        for index, row in enumerate(rows)
    )
    accepted_scan_values = [
        values
        for values in (
            tuple(choice) for choice in __import__("itertools").product(*predicate.accepted_values)
        )
    ]
    scan_origins = sorted({encode_scan(values) for values in accepted_scan_values})
    min_aggregate = min(row.aggregate_value for row in rows)
    max_aggregate = max(row.aggregate_value for row in rows)
    min_group_id = 0
    max_group_id = len(group_tuples) - 1
    width = (max_aggregate - min_aggregate + 2000) // 2000 + 1
    height = (max_group_id - min_group_id + 14) // 14
    if (max_group_id - min_group_id) % 14:
        height += 1
    rays = []
    ray_id = 0
    for scan_z in scan_origins:
        for y_index in range(height):
            for x_index in range(width):
                rays.append(
                    rt.Ray3D(
                        id=ray_id,
                        ox=float(x_index * 2000 + min_aggregate),
                        oy=float((y_index + 1) * 14),
                        oz=float(scan_z) - 0.5,
                        dx=0.0,
                        dy=0.0,
                        dz=1.0,
                        tmax=1.0,
                    )
                )
                ray_id += 1
    return {
        "rays": tuple(rays),
        "triangles": triangles,
        "primitive_group_ids": tuple(group_to_id[row.group_values] for row in rows),
        "primitive_values": tuple(row.aggregate_value for row in rows),
        "group_tuples": tuple(group_tuples),
        "scan_value_maps": tuple(scan_value_maps),
        "scan_origins": tuple(scan_origins),
        "width": width,
        "height": height,
        "depth": len(scan_origins),
    }


def lower_bounded_q21_to_generic_rt() -> dict[str, object]:
    return lower_rows_to_generic_rt(bounded_q21_rows(), bounded_q21_predicate())


def run_rtdl_bounded(backend: str) -> dict[str, object]:
    import rtdsl as rt

    if backend not in {"cpu", "optix"}:
        raise ValueError("bounded RTDL backend must be cpu or optix")
    workload = lower_bounded_q21_to_generic_rt()
    result = rt.run_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
        workload["rays"],
        workload["triangles"],
        primitive_group_ids=workload["primitive_group_ids"],
        primitive_values=workload["primitive_values"],
        reduction="sum",
        deduplicate_primitives=True,
        backend=backend,
        include_hit_primitive_indices=True,
    )
    group_tuples = workload["group_tuples"]
    actual_rows = [
        {
            "group": list(group_tuples[int(row["group_id"])]),
            "value": int(row["sum"]),
        }
        for row in result["rows"]
        if int(row["sum"]) != 0
    ]
    actual_rows.sort(key=lambda row: tuple(row["group"]))
    expected_rows = canonical_grouped_sum_rows(
        bounded_q21_rows(), bounded_q21_predicate()
    )
    return {
        "schema": "rtdl.paper_reproduction.raydb.bounded_rtdl_gate.v1",
        "case_id": "bounded_q21_grouped_sum_discriminator",
        "backend": backend,
        "generic_public_api": "run_generic_ray_triangle_primitive_grouped_i64_reduction_3d",
        "app_semantics_in_core": False,
        "ray_count": len(workload["rays"]),
        "triangle_count": len(workload["triangles"]),
        "launch_shape": [workload["width"], workload["height"], workload["depth"]],
        "deduplicate_primitives": True,
        "rtdl_rows": actual_rows,
        "expected_rows": expected_rows,
        "rtdl_matches_cpu_oracle": actual_rows == expected_rows,
        "missing_rows": [row for row in expected_rows if row not in actual_rows],
        "unexpected_rows": [row for row in actual_rows if row not in expected_rows],
        "primitive_result": {
            key: value
            for key, value in result.items()
            if key not in {"rows", "hit_primitive_indices"}
        },
        "claim_boundary": {
            "bounded_rtdl_correctness_claimed": False,
            "author_rtdl_equality_claimed": False,
            "ssb_query_claimed": False,
            "paper_performance_claimed": False,
        },
    }


def _pack_i32_column(values: Iterable[int]) -> bytes:
    packed = bytearray()
    for value in values:
        value = int(value)
        if not -(2**31) <= value < 2**31:
            raise ValueError(f"value is outside int32: {value}")
        packed.extend(struct.pack("<i", value))
    return bytes(packed)


def encode_author_binary(rows: Sequence[FlatRow]) -> bytes:
    if not rows:
        raise ValueError("at least one row is required")
    group_dims = len(rows[0].group_values)
    scan_dims = len(rows[0].scan_values)
    if group_dims < 1 or scan_dims < 1:
        raise ValueError("group and scan dimensions must be nonempty")
    for row in rows:
        if len(row.group_values) != group_dims or len(row.scan_values) != scan_dims:
            raise ValueError("all rows must have one fixed column schema")

    payload = bytearray(_pack_i32_column(row.aggregate_value for row in rows))
    for index in range(group_dims):
        payload.extend(_pack_i32_column(row.group_values[index] for row in rows))
    for index in range(scan_dims):
        payload.extend(_pack_i32_column(row.scan_values[index] for row in rows))
    return bytes(payload)


def encode_exact_list_predicate(predicate: ExactListPredicate) -> str:
    if not predicate.accepted_values:
        raise ValueError("at least one predicate dimension is required")
    lines = []
    types = []
    for accepted in predicate.accepted_values:
        if not accepted:
            raise ValueError("exact-list predicate dimensions cannot be empty")
        lines.append(",".join(str(int(value)) for value in accepted))
        types.append(str(len(accepted)))
    return "\n".join([*lines, ",".join(types)]) + "\n"


def parse_author_group_rows(stdout: str, group_dims: int) -> tuple[list[dict[str, object]], int]:
    in_results = False
    rows: list[dict[str, object]] = []
    line_num: int | None = None
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if line == "Result below:":
            in_results = True
            continue
        if not in_results:
            continue
        if line.startswith("Line Num :"):
            line_num = int(line.split(":", 1)[1].strip())
            break
        if not line or set(line) == {"-"}:
            continue
        parts = line.split()
        if len(parts) != group_dims + 1:
            raise ValueError(f"unexpected author result row: {raw_line!r}")
        values = [int(part) for part in parts]
        rows.append({"group": values[:group_dims], "value": values[-1]})
    if line_num is None:
        raise ValueError("author output did not contain Line Num")
    rows.sort(key=lambda row: tuple(int(value) for value in row["group"]))
    if line_num != len(rows):
        raise ValueError(
            f"author Line Num {line_num} differs from parsed rows {len(rows)}"
        )
    return rows, line_num


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_bounded_packet(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = bounded_q21_rows()
    predicate = bounded_q21_predicate()
    data_path = output_dir / "bounded_q21_data.bin"
    predicate_path = output_dir / "bounded_q21_predicate.txt"
    expected_path = output_dir / "bounded_q21_expected_rows.json"
    data_path.write_bytes(encode_author_binary(rows))
    predicate_path.write_text(encode_exact_list_predicate(predicate), encoding="ascii")
    expected_rows = canonical_grouped_sum_rows(rows, predicate)
    expected_path.write_text(json.dumps(expected_rows, indent=2) + "\n", encoding="utf-8")
    return {
        "schema": "rtdl.paper_reproduction.raydb.bounded_packet.v1",
        "case_id": "bounded_q21_grouped_sum_discriminator",
        "row_count": len(rows),
        "group_dimension_count": 2,
        "predicate_dimension_count": 2,
        "interval_x": 2000,
        "interval_y": 14,
        "author_cli": [
            "-n", str(len(rows)), "-x", "2000", "-y", "14",
            "-g", "2", "-p", "2", "-s", str(predicate_path),
            "-i", str(data_path),
        ],
        "data_sha256": sha256_file(data_path),
        "predicate_sha256": sha256_file(predicate_path),
        "expected_rows_sha256": sha256_file(expected_path),
        "expected_rows": expected_rows,
        "expected_line_num": len(expected_rows),
        "claim_boundary": {
            "bounded_author_correctness_claimed": False,
            "rtdl_equality_claimed": False,
            "ssb_query_claimed": False,
            "paper_performance_claimed": False,
        },
    }


def run_author(binary: Path, packet_dir: Path) -> dict[str, object]:
    packet = write_bounded_packet(packet_dir)
    command = [str(binary), *packet["author_cli"]]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"author failed with {completed.returncode}:\n{completed.stderr}\n{completed.stdout}"
        )
    actual_rows, line_num = parse_author_group_rows(completed.stdout, 2)
    expected_rows = packet["expected_rows"]
    return {
        **packet,
        "author_binary": str(binary),
        "author_binary_sha256": sha256_file(binary),
        "author_command": command,
        "author_returncode": completed.returncode,
        "author_rows": actual_rows,
        "author_line_num": line_num,
        "author_matches_cpu_oracle": actual_rows == expected_rows,
        "missing_rows": [row for row in expected_rows if row not in actual_rows],
        "unexpected_rows": [row for row in actual_rows if row not in expected_rows],
        "raw_stdout": completed.stdout,
        "raw_stderr": completed.stderr,
    }


def run_author_packet(binary: Path, packet_json: Path) -> dict[str, object]:
    packet = json.loads(packet_json.read_text(encoding="utf-8"))
    packet_schema = str(packet.get("schema", ""))
    packet_json_sha256 = sha256_file(packet_json)
    packet_hashes_before = _packet_file_hashes(packet)
    command = [str(binary), *[str(value) for value in packet["author_cli"]]]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    packet_hashes_after = _packet_file_hashes(packet)
    if packet_hashes_after != packet_hashes_before:
        raise RuntimeError("packet files changed while the author process was executing")
    if completed.returncode != 0:
        raise RuntimeError(
            f"author failed with {completed.returncode}:\n{completed.stderr}\n{completed.stdout}"
        )
    actual_rows, line_num = parse_author_group_rows(
        completed.stdout, int(packet["group_dimension_count"])
    )
    expected_rows = packet["expected_rows"]
    claim_boundary = dict(packet.get("claim_boundary", {}))
    claim_boundary["author_executed"] = True
    return {
        **packet,
        "schema": "rtdl.paper_reproduction.raydb.author_packet_gate.v2",
        "packet_schema": packet_schema,
        "packet_json_sha256": packet_json_sha256,
        "packet_file_hashes_before": packet_hashes_before,
        "packet_file_hashes_after": packet_hashes_after,
        "packet_files_stable_during_author_run": True,
        "runner_sha256": sha256_file(Path(__file__)),
        "execution_identity": {
            "evidence_cohort_id": os.environ.get("RTDL_EVIDENCE_COHORT_ID"),
            "host": socket.gethostname(),
            "gpu_identity": _observed_gpu_identity(),
            "matrix_runner_sha256": os.environ.get(
                "RTDL_EVIDENCE_MATRIX_RUNNER_SHA256"
            ),
        },
        "author_binary": str(binary),
        "author_binary_sha256": sha256_file(binary),
        "author_source_identity": _author_source_identity(binary),
        "author_command": command,
        "author_returncode": completed.returncode,
        "author_rows": actual_rows,
        "author_line_num": line_num,
        "author_matches_cpu_oracle": actual_rows == expected_rows,
        "missing_rows": [row for row in expected_rows if row not in actual_rows],
        "unexpected_rows": [row for row in actual_rows if row not in expected_rows],
        "claim_boundary": claim_boundary,
        "raw_stdout": completed.stdout,
        "raw_stderr": completed.stderr,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RayDB paper-app bounded gate tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build-bounded-packet")
    build_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser = subparsers.add_parser("run-author-bounded")
    run_parser.add_argument("--author-binary", type=Path, required=True)
    run_parser.add_argument("--packet-dir", type=Path, required=True)
    run_parser.add_argument("--output-json", type=Path, required=True)
    packet_parser = subparsers.add_parser("run-author-packet")
    packet_parser.add_argument("--author-binary", type=Path, required=True)
    packet_parser.add_argument("--packet-json", type=Path, required=True)
    packet_parser.add_argument("--output-json", type=Path, required=True)
    rtdl_parser = subparsers.add_parser("run-rtdl-bounded")
    rtdl_parser.add_argument("--backend", choices=("cpu", "optix"), required=True)
    rtdl_parser.add_argument("--author-result", type=Path, required=True)
    rtdl_parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.command == "build-bounded-packet":
        print(json.dumps(write_bounded_packet(args.output_dir), indent=2))
        return 0
    if args.command == "run-rtdl-bounded":
        result = run_rtdl_bounded(args.backend)
        author = json.loads(args.author_result.read_text(encoding="utf-8"))
        result["author_rows"] = author["author_rows"]
        result["author_result_sha256"] = sha256_file(args.author_result)
        result["same_input_hashes"] = {
            "data_sha256": author["data_sha256"],
            "predicate_sha256": author["predicate_sha256"],
        }
        result["author_rtdl_complete_group_rows_equal"] = (
            result["rtdl_rows"] == author["author_rows"]
        )
        result["claim_boundary"]["bounded_rtdl_correctness_claimed"] = bool(
            result["rtdl_matches_cpu_oracle"]
        )
        result["claim_boundary"]["author_rtdl_equality_claimed"] = bool(
            result["author_rtdl_complete_group_rows_equal"]
        )
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0 if (
            result["rtdl_matches_cpu_oracle"]
            and result["author_rtdl_complete_group_rows_equal"]
        ) else 1

    if args.command == "run-author-packet":
        result = run_author_packet(args.author_binary, args.packet_json)
        _write_json_atomic(args.output_json, result)
        print(json.dumps({key: value for key, value in result.items() if not key.startswith("raw_")}, indent=2))
        return 0 if result["author_matches_cpu_oracle"] else 1

    result = run_author(args.author_binary, args.packet_dir)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if not key.startswith("raw_")}, indent=2))
    return 0 if result["author_matches_cpu_oracle"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
