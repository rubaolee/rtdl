#!/usr/bin/env python3
"""Project-import-free recount of the post-formal CPU sensitivity study."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import defaultdict
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any


SOURCE_COMMIT = "02e84374fc092d2bb916cca633eda9592b4ecf07"
SOURCE_TREE = "8aad15d686bbc9e1c3b11df998898a0a063a01f1"
SOURCE_ROOT = "/tmp/rtdl-v4-affinity-02e84374f"
NATIVE_LIBRARY_PATH = (
    "/workspace/rtdl-v4-long-perf-successor-5f07cce58/librtdl_optix.so"
)
NATIVE_LIBRARY_SHA256 = (
    "5edb9ec3e542b64bf0696c6df9a164448aecd6b5b51f1fdd78ba6e8c791dd2af"
)
BASE_CONFIG_SHA256 = (
    "491d399343fee27fbf97f6a72837ff38b4b7d04fa5324525cf3b3780caf72e1d"
)
WORKER_SHA256 = (
    "0009137c032dc13f03065898283c95ed087153eb11a36a69723fea32a4b7ed50"
)
BASE_WORKER_SHA256 = (
    "ebcb71ccf9d86e9405205564fa979283f102d43a190a04d602f61ea1eb23ab9e"
)
CONTROLLER_SHA256 = (
    "c7072ce8867f9dd11f0719daa52336636440525bd272fae64b1e646863a6c0bd"
)
PLAN_COMMIT = "c54bce034"
PYTHON_EXECUTABLE = "/workspace/rtdl-v4-paper-apps-run/venv/bin/python"
PYTHON_EXECUTABLE_SHA256 = (
    "1d3cf64f97cadc79fdc6fe2496a21b7b456cb94211978cfef5a65f616af74fd5"
)
GPU = {
    "compute_capability": "8.6",
    "driver": "550.127.05",
    "name": "NVIDIA RTX A4500",
    "uuid": "GPU-5dbda20d-af85-650e-7250-10b265a77143",
}
ARMS = ("new_v4", "pyoptix")
BLOCK_ORDERS = (("new_v4", "pyoptix"), ("pyoptix", "new_v4"))
UNIT_CONTRACTS = {
    "particle_tracking": {
        "app": "particle_tracking",
        "operation": None,
        "repetitions": 32,
        "output_sha256": (
            "81dea3f2ad83c6c239a372d699b6133a088fe7171356b298b9aeace4074370c7"
        ),
    },
    "librts__parks__range_contains": {
        "app": "librts",
        "operation": "range_contains",
        "repetitions": 4,
        "output_sha256": (
            "ce12d9de8ed2fb51211f9c192801f0c32744edd6d18e9576b453afcc4f37b687"
        ),
    },
}
HASH_LISTINGS = {
    "configs": "CONFIGS.sha256",
    "journals": "JOURNALS.sha256",
    "launches": "LAUNCHES.sha256",
    "stderr": "STDERR.sha256",
    "stdout": "STDOUT.sha256",
    "workers": "WORKERS.sha256",
}
PROGRESS_FIELDS = (
    "ordinal", "cpu", "unit", "block", "position", "arm",
    "return_code", "output_sha256", "journal_sha256", "stdout_sha256",
    "stderr_sha256",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class RecountError(RuntimeError):
    """The retained sensitivity population is incomplete or inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RecountError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def strict_loads(payload: str, label: str) -> Any:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise RecountError(f"duplicate JSON key in {label}: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise RecountError(f"non-finite JSON value in {label}: {value}")

    try:
        return json.loads(
            payload,
            object_pairs_hook=object_pairs,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as error:
        raise RecountError(f"cannot parse strict JSON {label}: {error}") from error


def strict_json(path: Path) -> Any:
    try:
        payload = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise RecountError(f"cannot read strict JSON {path}: {error}") from error
    return strict_loads(payload, str(path))


def read_object(path: Path) -> dict[str, Any]:
    value = strict_json(path)
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def read_journal(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise RecountError(f"cannot read journal {path}: {error}") from error
    for line_number, line in enumerate(lines, start=1):
        require(bool(line), f"blank journal line: {path}:{line_number}")
        try:
            value = strict_loads(line, f"{path}:{line_number}")
        except RecountError as error:
            raise RecountError(
                f"invalid journal row: {path}:{line_number}: {error}"
            ) from error
        require(isinstance(value, dict),
                f"journal row is not an object: {path}:{line_number}")
        rows.append(value)
    return rows


def expected_schedule() -> list[dict[str, Any]]:
    rows = []
    for cpu in range(48):
        for unit, contract in UNIT_CONTRACTS.items():
            for block, order in enumerate(BLOCK_ORDERS):
                for position, arm in enumerate(order):
                    rows.append({
                        "ordinal": len(rows),
                        "cpu": cpu,
                        "unit": unit,
                        "endpoint": "prepared",
                        "block": block,
                        "position": position,
                        "arm": arm,
                        "repetitions": contract["repetitions"],
                        "warmups": 1,
                        "timeout_seconds": 900,
                        "config_relative": f"configs/CONFIG_CPU_{cpu:02d}.json",
                    })
    require(len(rows) == 384, "independent schedule does not contain 384 rows")
    return rows


def stem(row: Mapping[str, Any]) -> str:
    return (
        f"w{row['ordinal']:03d}__cpu{row['cpu']:02d}__{row['unit']}"
        f"__b{row['block']}__p{row['position']}__{row['arm']}"
    )


def verify_topology(root: Path) -> None:
    cpuset_pre = (root / "CPUSET_PRE.txt").read_text(encoding="utf-8")
    cpuset_post = (root / "CPUSET_POST.txt").read_text(encoding="utf-8")
    for label, payload in (("pre", cpuset_pre), ("post", cpuset_post)):
        require("Cpus_allowed_list:\t0-47" in payload,
                f"allowed CPU list differs: {label}")
        require("Mems_allowed_list:\t0" in payload,
                f"allowed memory node differs: {label}")

    lines = (root / "CPU_TOPOLOGY.txt").read_text(
        encoding="utf-8",
    ).splitlines()
    require(lines and lines[0].split() == ["CPU", "CORE", "SOCKET", "NODE", "ONLINE"],
            "CPU topology header differs")
    rows = [line.split() for line in lines[1:] if line.strip()]
    require(len(rows) == 48, "CPU topology does not contain 48 logical CPUs")
    for cpu, row in enumerate(rows):
        require(row == [str(cpu), str(cpu % 24), "0", "0", "yes"],
                f"CPU topology differs: {cpu}")


def read_hash_listing(path: Path, expected_files: set[str]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1,
    ):
        pieces = line.split(maxsplit=1)
        require(len(pieces) == 2 and HEX64.fullmatch(pieces[0]) is not None,
                f"invalid hash-list row: {path}:{line_number}")
        name = Path(pieces[1].strip()).name
        require(name not in observed, f"duplicate hash-list member: {path}:{name}")
        observed[name] = pieces[0]
    require(set(observed) == expected_files,
            f"hash-list member set differs: {path}")
    return observed


def read_single_hash_sidecar(path: Path, expected_name: str) -> str:
    pieces = path.read_text(encoding="utf-8").strip().split(maxsplit=1)
    require(len(pieces) == 2 and HEX64.fullmatch(pieces[0]) is not None,
            f"invalid hash sidecar: {path}")
    require(Path(pieces[1]).name == expected_name,
            f"hash sidecar name differs: {path}")
    return pieces[0]


def verify_configs(
    root: Path, schedule_rows: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    config_dir = root / "configs"
    expected_names = {f"CONFIG_CPU_{cpu:02d}.json" for cpu in range(48)}
    members = list(config_dir.iterdir())
    require(all(path.is_file() and not path.is_symlink() for path in members),
            "configuration directory contains a non-regular member")
    observed_names = {path.name for path in members}
    require(observed_names == expected_names, "configuration file set differs")
    listing = read_hash_listing(root / HASH_LISTINGS["configs"], expected_names)
    by_cpu: dict[int, dict[str, Any]] = {}
    normalized_digest: str | None = None
    for cpu in range(48):
        path = config_dir / f"CONFIG_CPU_{cpu:02d}.json"
        require(sha256(path) == listing[path.name], f"config hash differs: {cpu}")
        config = read_object(path)
        require(config.get("schema") == "rtdl.v4_long_workload.formal_config.v1",
                f"config schema differs: {cpu}")
        common = config.get("common")
        require(isinstance(common, dict), f"config common section differs: {cpu}")
        require(common.get("cpu_affinity") == {"cpu_ids": [cpu]},
                f"config affinity differs: {cpu}")
        require(common.get("registered_machine") == {
            "cuda_visible_devices": "0", "gpu": GPU,
        }, f"config registered machine differs: {cpu}")
        implementations = config.get("implementations")
        require(isinstance(implementations, dict),
                f"config implementations differ: {cpu}")
        for arm in ARMS:
            implementation = implementations.get(arm)
            require(isinstance(implementation, dict),
                    f"config implementation missing: {cpu}:{arm}")
            require(implementation.get("source_commit") == SOURCE_COMMIT
                    and implementation.get("source_tree") == SOURCE_TREE
                    and implementation.get("source_root") == SOURCE_ROOT
                    and implementation.get("native_library_path")
                    == NATIVE_LIBRARY_PATH
                    and implementation.get("native_library_sha256")
                    == NATIVE_LIBRARY_SHA256,
                    f"config implementation identity differs: {cpu}:{arm}")
        units = config.get("units")
        require(isinstance(units, dict), f"config unit section differs: {cpu}")
        for unit, contract in UNIT_CONTRACTS.items():
            unit_row = units.get(unit)
            require(isinstance(unit_row, dict), f"config unit missing: {cpu}:{unit}")
            require(unit_row.get("unit_id") == unit
                    and unit_row.get("app") == contract["app"]
                    and unit_row.get("operation") == contract["operation"]
                    and unit_row.get("prepared_repetitions")
                    == contract["repetitions"],
                    f"config unit contract differs: {cpu}:{unit}")
        normalized = deepcopy(config)
        normalized["common"]["cpu_affinity"] = {"cpu_ids": ["CPU"]}
        current = canonical_digest(normalized)
        if normalized_digest is None:
            normalized_digest = current
        require(current == normalized_digest,
                f"config differs beyond CPU affinity: {cpu}")
        by_cpu[cpu] = config

    hashes_by_cpu = {
        int(row["cpu"]): row["config_sha256"] for row in schedule_rows
    }
    require(len(hashes_by_cpu) == 48, "schedule config population differs")
    for cpu, config in by_cpu.items():
        require(hashes_by_cpu[cpu] == sha256(
            config_dir / f"CONFIG_CPU_{cpu:02d}.json"
        ), f"schedule config hash differs: {cpu}")
    return by_cpu


def verify_schedule(root: Path) -> list[dict[str, Any]]:
    expected_rows = expected_schedule()
    schedule_path = root / "SCHEDULE.json"
    schedule = read_object(schedule_path)
    require(set(schedule) == {
        "schema", "formal_evidence", "pooling_into_formal_transaction_forbidden",
        "preregistered_plan_commit", "base_config_sha256", "worker_count",
        "retry_allowed", "discard_allowed", "rows",
    }, "schedule fields differ")
    require(schedule.get("schema")
            == "rtdl.v4_long_workload.cpu_sensitivity.schedule.v1",
            "schedule schema differs")
    require(schedule.get("formal_evidence") is False
            and schedule.get("pooling_into_formal_transaction_forbidden") is True,
            "schedule evidence boundary differs")
    require(schedule.get("preregistered_plan_commit") == PLAN_COMMIT,
            "schedule plan identity differs")
    require(schedule.get("base_config_sha256") == BASE_CONFIG_SHA256,
            "schedule base-config identity differs")
    require(schedule.get("worker_count") == 384,
            "schedule worker count differs")
    require(schedule.get("retry_allowed") is False
            and schedule.get("discard_allowed") is False,
            "schedule retry/discard contract differs")
    observed_rows = schedule.get("rows")
    require(isinstance(observed_rows, list) and len(observed_rows) == 384,
            "schedule row population differs")
    for expected, observed in zip(expected_rows, observed_rows, strict=True):
        expected_with_hash = {
            **expected,
            "config_sha256": sha256(root / expected["config_relative"]),
        }
        require(observed == expected_with_hash,
                f"schedule row differs: {expected['ordinal']}")

    schedule_hash = sha256(schedule_path)
    require((root / "SCHEDULE.sha256").read_text(encoding="utf-8")
            == f"{schedule_hash}  SCHEDULE.json\n",
            "schedule hash sidecar differs")
    expected_tsv = "".join("\t".join(str(row[key]) for key in (
        "ordinal", "cpu", "unit", "block", "position", "arm",
        "repetitions", "warmups", "timeout_seconds", "config_relative",
    )) + "\n" for row in expected_rows)
    tsv_path = root / "SCHEDULE.tsv"
    require(tsv_path.read_text(encoding="utf-8") == expected_tsv,
            "schedule TSV differs")
    require(read_single_hash_sidecar(
        root / "SCHEDULE_TSV.sha256", "SCHEDULE.tsv",
    ) == sha256(tsv_path),
            "schedule TSV hash sidecar differs")
    return observed_rows


def verify_directory_hashes(root: Path, expected_stems: set[str]) -> None:
    extensions = {
        "workers": ".json", "journals": ".jsonl", "launches": ".json",
        "stdout": ".bin", "stderr": ".bin",
    }
    for directory, extension in extensions.items():
        expected_names = {name + extension for name in expected_stems}
        members = list((root / directory).iterdir())
        require(all(path.is_file() and not path.is_symlink() for path in members),
                f"raw directory contains a non-regular member: {directory}")
        observed_names = {path.name for path in members}
        require(observed_names == expected_names,
                f"raw member set differs: {directory}")
        listing = read_hash_listing(root / HASH_LISTINGS[directory], expected_names)
        for name in expected_names:
            require(sha256(root / directory / name) == listing[name],
                    f"raw hash-list identity differs: {directory}/{name}")


def read_progress(root: Path) -> list[dict[str, str]]:
    with (root / "CONTROLLER_PROGRESS.tsv").open(
        encoding="utf-8", newline="",
    ) as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(tuple(reader.fieldnames or ()) == PROGRESS_FIELDS,
                "progress header differs")
        rows = list(reader)
    require(len(rows) == 384, "progress population differs")
    return rows


def validate_worker_machine(worker: Mapping[str, Any], cpu: int) -> None:
    machine = worker.get("machine")
    require(isinstance(machine, Mapping), f"worker machine missing: CPU {cpu}")
    require(machine.get("cuda_visible_devices") == "0"
            and machine.get("gpu") == GPU,
            f"worker GPU identity differs: CPU {cpu}")
    require(machine.get("python") == "3.12.3",
            f"worker Python identity differs: CPU {cpu}")
    require(machine.get("python_executable") == PYTHON_EXECUTABLE,
            f"worker Python executable differs: CPU {cpu}")
    require(machine.get("cpu_affinity") == {
        "preflight": {"cpu_ids": [cpu]},
        "postflight": {"cpu_ids": [cpu]},
    }, f"worker affinity differs: CPU {cpu}")


def validate_worker(
    *, row: Mapping[str, Any], launch: Mapping[str, Any],
    worker: Mapping[str, Any], journal: list[dict[str, Any]],
) -> None:
    ordinal = int(row["ordinal"])
    unit = str(row["unit"])
    cpu = int(row["cpu"])
    contract = UNIT_CONTRACTS[unit]
    require(worker.get("schema") == "rtdl.v4_long_workload.worker_result.v1",
            f"worker schema differs: {ordinal}")
    require(worker.get("status") == "PASS", f"worker status differs: {ordinal}")
    require(worker.get("unit_id") == unit
            and worker.get("app") == contract["app"]
            and worker.get("operation") == contract["operation"]
            and worker.get("endpoint") == "prepared"
            and worker.get("arm") == row["arm"],
            f"worker task identity differs: {ordinal}")
    require(worker.get("formal_config_sha256") == row["config_sha256"],
            f"worker config identity differs: {ordinal}")
    require(worker.get("formal_worker_sha256") == WORKER_SHA256,
            f"worker executable identity differs: {ordinal}")
    require(worker.get("retry_count") == 0 and worker.get("discard_count") == 0,
            f"worker retry/discard differs: {ordinal}")
    require(worker.get("warmup_count") == 1,
            f"worker warmup count differs: {ordinal}")
    samples = worker.get("primary_samples_ns")
    require(isinstance(samples, list)
            and len(samples) == row["repetitions"]
            and all(type(value) is int and value > 0 for value in samples),
            f"worker timing population differs: {ordinal}")
    require(worker.get("execute_samples_ns") == samples,
            f"worker execute samples differ: {ordinal}")
    require(worker.get("retained_sample_count") == len(samples),
            f"worker retained sample count differs: {ordinal}")
    require(worker.get("primary_median_ns") == int(statistics.median(samples)),
            f"worker median differs: {ordinal}")
    require(worker.get("input_load_included_in_primary_timer") is False
            and worker.get("journal_io_included_in_primary_timer") is False
            and worker.get("complete_timer_includes_prepare_execute_close") is False,
            f"worker timing boundary differs: {ordinal}")
    require(worker.get("output_sha256") == contract["output_sha256"],
            f"worker output identity differs: {ordinal}")
    outputs = worker.get("outputs")
    require(isinstance(outputs, list) and len(outputs) == row["repetitions"],
            f"worker output population differs: {ordinal}")
    for output in outputs:
        require(isinstance(output, dict)
                and output.get("matched") is True
                and output.get("output_sha256") == contract["output_sha256"],
                f"worker output oracle differs: {ordinal}")
    validate_worker_machine(worker, cpu)
    identity = worker.get("implementation_identity")
    require(isinstance(identity, Mapping),
            f"worker implementation identity missing: {ordinal}")
    require(identity.get("source_commit") == SOURCE_COMMIT
            and identity.get("source_tree") == SOURCE_TREE
            and identity.get("source_root") == SOURCE_ROOT
            and identity.get("source_status_clean") is True
            and identity.get("native_library_path") == NATIVE_LIBRARY_PATH
            and identity.get("native_library_sha256") == NATIVE_LIBRARY_SHA256
            and identity.get("base_worker_sha256") == BASE_WORKER_SHA256,
            f"worker implementation identity differs: {ordinal}")
    runtime = worker.get("runtime_identity")
    require(isinstance(runtime, Mapping)
            and runtime.get("python_version") == "3.12.3"
            and runtime.get("python_executable") == PYTHON_EXECUTABLE
            and runtime.get("python_executable_sha256")
            == PYTHON_EXECUTABLE_SHA256,
            f"worker runtime identity differs: {ordinal}")
    require(worker.get("journal_sha256") == launch.get("journal_sha256"),
            f"worker journal identity differs: {ordinal}")

    require(journal and journal[0].get("event") == "worker_started"
            and journal[0].get("pid") == worker.get("process_id"),
            f"journal start differs: {ordinal}")
    for phase in ("preflight", "postflight"):
        events = [entry for entry in journal
                  if entry.get("event") == f"cpu_affinity_{phase}"]
        require(len(events) == 1
                and events[0].get("observation") == {"cpu_ids": [cpu]},
                f"journal affinity differs: {ordinal}:{phase}")
    warmups = [entry for entry in journal if entry.get("event") == "warmup_complete"]
    timed = [entry for entry in journal if entry.get("event") == "sample_complete"]
    closes = [entry for entry in journal if entry.get("event") == "close_complete"]
    require(len(warmups) == 1 and len(timed) == row["repetitions"]
            and len(closes) == 1,
            f"journal event population differs: {ordinal}")
    require([entry.get("elapsed_ns") for entry in timed] == samples,
            f"journal timing samples differ: {ordinal}")


def summarize_population(rows: list[dict[str, Any]]) -> dict[str, Any]:
    medians = [float(row["median_new_v4_over_pyoptix"]) for row in rows]
    return {
        "cpu_count": len(rows),
        "median_of_cpu_medians": statistics.median(medians),
        "minimum_cpu_median": min(medians),
        "maximum_cpu_median": max(medians),
        "count_cpu_medians_lte_1_20": sum(value <= 1.20 for value in medians),
        "count_cpus_both_blocks_lte_1_35": sum(
            bool(row["both_blocks_lte_1_35"]) for row in rows
        ),
    }


def recount(root: Path, controller_script: Path) -> dict[str, Any]:
    expected_root_members = {
        "BASE_CONFIG.sha256", "CGROUP_PRE.txt", "COMPLETED_AT.txt",
        "CONFIGS.sha256", "CONTROLLER_PROGRESS.tsv", "CPUSET_POST.txt",
        "CPUSET_PRE.txt", "CPU_TOPOLOGY.txt", "GPU_PROCESSES_POST.txt",
        "GPU_PROCESSES_PRE.txt", "JOURNALS.sha256", "LAST_COMPLETED_ORDINAL.txt",
        "LAUNCHES.sha256", "LSCPU.txt", "NVIDIA_SMI_POST.txt",
        "NVIDIA_SMI_PRE.txt", "RAW_COMPLETE.txt", "SCHEDULE.json",
        "SCHEDULE.sha256", "SCHEDULE.tsv", "SCHEDULE_TSV.sha256",
        "SOURCE_COMMIT.txt", "SOURCE_STATUS.txt", "SOURCE_TREE.txt",
        "STARTED_AT.txt", "STDERR.sha256", "STDOUT.sha256", "WORKERS.sha256",
        "configs", "journals", "launches", "stderr", "stdout", "workers",
    }
    members = list(root.iterdir())
    require(all(not path.is_symlink() for path in members),
            "raw root contains a symlink")
    require({path.name for path in members} == expected_root_members,
            "raw root member set differs")
    raw_complete = root / "RAW_COMPLETE.txt"
    require(raw_complete.is_file(), "raw-complete marker is missing")
    require(raw_complete.read_text(encoding="utf-8")
            == "PASS__RAW_POPULATION_COMPLETE\n",
            "raw-complete marker differs")
    require((root / "SOURCE_COMMIT.txt").read_text(encoding="utf-8").strip()
            == SOURCE_COMMIT, "source commit differs")
    require((root / "SOURCE_TREE.txt").read_text(encoding="utf-8").strip()
            == SOURCE_TREE, "source tree differs")
    require(not (root / "SOURCE_STATUS.txt").read_text(encoding="utf-8"),
            "measured source checkout was dirty")
    require(read_single_hash_sidecar(
        root / "BASE_CONFIG.sha256",
        "FORMAL_CONFIG_02E84374F_A4500_CPU8_V2.json",
    ) == BASE_CONFIG_SHA256, "base-config hash sidecar differs")
    require((root / "LAST_COMPLETED_ORDINAL.txt").read_text(
        encoding="utf-8",
    ) == "383\n", "last-completed ordinal differs")
    for name in (
        "STARTED_AT.txt", "COMPLETED_AT.txt", "LSCPU.txt", "CGROUP_PRE.txt",
        "NVIDIA_SMI_PRE.txt", "NVIDIA_SMI_POST.txt", "GPU_PROCESSES_PRE.txt",
        "GPU_PROCESSES_POST.txt",
    ):
        require((root / name).is_file(), f"required machine snapshot missing: {name}")
    require((root / "GPU_PROCESSES_PRE.txt").read_bytes() == b"",
            "a compute process was present before the sensitivity study")
    require((root / "CGROUP_PRE.txt").read_text(encoding="utf-8") == (
        "/sys/fs/cgroup/cpu/cpu.cfs_quota_us=1020000\n"
        "/sys/fs/cgroup/cpu/cpu.cfs_period_us=100000\n"
        "/sys/fs/cgroup/cpuset/cpuset.cpus=0-47\n"
    ), "cgroup contract differs")
    require(sha256(controller_script) == CONTROLLER_SHA256,
            "controller script identity differs")
    verify_topology(root)
    schedule_rows = verify_schedule(root)
    verify_configs(root, schedule_rows)
    expected_stems = {stem(row) for row in schedule_rows}
    verify_directory_hashes(root, expected_stems)
    progress_rows = read_progress(root)

    process_ids: set[int] = set()
    cells: dict[tuple[int, str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row, progress in zip(schedule_rows, progress_rows, strict=True):
        ordinal = int(row["ordinal"])
        name = stem(row)
        require(all(progress[field] == str(row[field]) for field in (
            "ordinal", "cpu", "unit", "block", "position", "arm",
        )), f"progress schedule differs: {ordinal}")
        require(progress["return_code"] == "0",
                f"progress return code differs: {ordinal}")
        launch_path = root / "launches" / f"{name}.json"
        output_path = root / "workers" / f"{name}.json"
        journal_path = root / "journals" / f"{name}.jsonl"
        stdout_path = root / "stdout" / f"{name}.bin"
        stderr_path = root / "stderr" / f"{name}.bin"
        launch = read_object(launch_path)
        for field in ("ordinal", "cpu", "unit", "block", "position", "arm"):
            require(launch.get(field) == row[field],
                    f"launch schedule differs: {ordinal}:{field}")
        require(launch.get("schema")
                == "rtdl.v4_long_workload.cpu_sensitivity.launch.v1"
                and launch.get("return_code") == 0
                and launch.get("timeout") is False,
                f"launch status differs: {ordinal}")
        require(type(launch.get("started_epoch_ns")) is int
                and type(launch.get("ended_epoch_ns")) is int
                and launch["ended_epoch_ns"] > launch["started_epoch_ns"]
                and launch.get("wall_ns")
                == launch["ended_epoch_ns"] - launch["started_epoch_ns"],
                f"launch timing differs: {ordinal}")
        paths = {
            "output": output_path, "journal": journal_path,
            "stdout": stdout_path, "stderr": stderr_path,
        }
        for field, path in paths.items():
            observed_hash = sha256(path)
            require(launch.get(f"{field}_sha256") == observed_hash
                    and progress[f"{field}_sha256"] == observed_hash,
                    f"launch/progress hash differs: {ordinal}:{field}")
        worker = read_object(output_path)
        journal = read_journal(journal_path)
        validate_worker(
            row=row, launch=launch, worker=worker, journal=journal,
        )
        pid = worker.get("process_id")
        require(type(pid) is int and pid > 0 and pid not in process_ids,
                f"worker PID is invalid or reused: {ordinal}")
        process_ids.add(pid)
        key = (int(row["cpu"]), str(row["unit"]), int(row["block"]))
        require(str(row["arm"]) not in cells[key],
                f"duplicate cell arm: {key}:{row['arm']}")
        cells[key][str(row["arm"])] = worker

    require(len(process_ids) == 384 and len(cells) == 192,
            "worker or cell population differs")
    cpu_rows: list[dict[str, Any]] = []
    for unit in UNIT_CONTRACTS:
        unit_input_identities: set[str] = set()
        for cpu in range(48):
            block_rows = []
            for block in range(2):
                by_arm = cells[(cpu, unit, block)]
                require(set(by_arm) == set(ARMS),
                        f"cell arm population differs: {cpu}:{unit}:{block}")
                input_digests = {
                    canonical_digest(worker["input_identity"])
                    for worker in by_arm.values()
                }
                output_hashes = {
                    str(worker["output_sha256"]) for worker in by_arm.values()
                }
                require(len(input_digests) == 1,
                        f"cell input identity differs: {cpu}:{unit}:{block}")
                require(output_hashes == {UNIT_CONTRACTS[unit]["output_sha256"]},
                        f"cell output identity differs: {cpu}:{unit}:{block}")
                unit_input_identities.update(input_digests)
                medians = {
                    arm: int(statistics.median(by_arm[arm]["primary_samples_ns"]))
                    for arm in ARMS
                }
                block_rows.append({
                    "block": block,
                    "order": list(BLOCK_ORDERS[block]),
                    "arm_medians_ns": medians,
                    "new_v4_over_pyoptix": (
                        medians["new_v4"] / medians["pyoptix"]
                    ),
                })
            ratios = [row["new_v4_over_pyoptix"] for row in block_rows]
            cpu_rows.append({
                "unit_id": unit,
                "cpu": cpu,
                "hardware_thread_class": "primary" if cpu < 24 else "smt_sibling",
                "blocks": block_rows,
                "median_new_v4_over_pyoptix": statistics.median(ratios),
                "minimum_block_ratio": min(ratios),
                "maximum_block_ratio": max(ratios),
                "median_lte_1_20": statistics.median(ratios) <= 1.20,
                "both_blocks_lte_1_35": max(ratios) <= 1.35,
            })
        require(len(unit_input_identities) == 1,
                f"input identity changes across CPUs: {unit}")

    summaries = []
    for unit in UNIT_CONTRACTS:
        selected = [row for row in cpu_rows if row["unit_id"] == unit]
        primary = [row for row in selected if row["cpu"] < 24]
        siblings = [row for row in selected if row["cpu"] >= 24]
        cpu8 = next(row for row in selected if row["cpu"] == 8)
        cpu8_value = float(cpu8["median_new_v4_over_pyoptix"])
        tie_count = sum(
            float(row["median_new_v4_over_pyoptix"]) == cpu8_value
            for row in selected
        )
        summaries.append({
            "unit_id": unit,
            "all_logical_cpus": summarize_population(selected),
            "primary_hardware_threads_0_23": summarize_population(primary),
            "smt_siblings_24_47": summarize_population(siblings),
            "cpu_8": {
                **cpu8,
                "ascending_rank_1_is_lowest": 1 + sum(
                    float(row["median_new_v4_over_pyoptix"]) < cpu8_value
                    for row in selected
                ),
                "exact_tie_count": tie_count,
            },
        })

    return {
        "schema": "rtdl.v4_long_workload.cpu_sensitivity.recount.v1",
        "status": "PASS__POST_FORMAL_DESCRIPTIVE_CPU_SENSITIVITY_RECOUNT",
        "formal_evidence": False,
        "pooled_into_formal_transaction": False,
        "project_modules_imported": False,
        "worker_count": 384,
        "distinct_process_id_count": len(process_ids),
        "paired_cell_count": len(cells),
        "logical_cpu_count": 48,
        "unit_count": 2,
        "retry_count": 0,
        "discard_count": 0,
        "timeout_count": 0,
        "all_raw_file_hashes_verified": True,
        "all_journals_reconstructed": True,
        "all_input_and_output_parity_verified": True,
        "cpu_rows": cpu_rows,
        "unit_summaries": summaries,
        "identities": {
            "source_commit": SOURCE_COMMIT,
            "source_tree": SOURCE_TREE,
            "native_library_sha256": NATIVE_LIBRARY_SHA256,
            "base_config_sha256": BASE_CONFIG_SHA256,
            "worker_sha256": WORKER_SHA256,
            "controller_sha256": CONTROLLER_SHA256,
            "schedule_sha256": sha256(root / "SCHEDULE.json"),
            "progress_sha256": sha256(root / "CONTROLLER_PROGRESS.tsv"),
            "raw_complete_sha256": sha256(root / "RAW_COMPLETE.txt"),
        },
        "claim_boundary": {
            "changes_formal_transaction": False,
            "confidence_interval_claimed": False,
            "cross_hardware_generalization_claimed": False,
            "formal_gate_inferred": False,
            "public_or_manuscript_claim_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--controller-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.raw_root.resolve(strict=True)
    controller = args.controller_script.resolve(strict=True)
    output = args.output.resolve(strict=False)
    require(root.is_dir(), "raw root is not a directory")
    require(controller.is_file(), "controller script is not a regular file")
    require(not output.exists(), "output already exists")
    require(output != root and root not in output.parents,
            "recount output must remain outside the raw directory")
    payload = recount(root, controller)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({
        "status": payload["status"],
        "output": str(output),
        "output_sha256": sha256(output),
        "worker_count": payload["worker_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RecountError, OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True))
        raise SystemExit(1)
