#!/usr/bin/env python3
"""Project-import-free recount of the cit-Patents replication transaction."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections.abc import Mapping
from pathlib import Path
from typing import Any


CONFIG_SCHEMA = "rtdl.v4_long_workload.formal_config.v1"
PREREG_SCHEMA = "rtdl.v4_long_workload.replication_preregistration.v1"
SCHEDULE_SCHEMA = "rtdl.v4_long_workload.replication_schedule.v1"
SUMMARY_SCHEMA = "rtdl.v4_long_workload.replication_summary.v1"
JOURNAL_SCHEMA = "rtdl.v4_long_workload.worker_journal.v1"
UNIT_ID = "triangle_counting__cit_patents__rt_2a1__4m"
ENDPOINT = "prepared"
ARMS = ("new_v4", "pyoptix")
BLOCK_ORDERS = (
    ("new_v4", "pyoptix"),
    ("pyoptix", "new_v4"),
    ("new_v4", "pyoptix"),
    ("pyoptix", "new_v4"),
    ("new_v4", "pyoptix"),
    ("pyoptix", "new_v4"),
    ("new_v4", "pyoptix"),
    ("pyoptix", "new_v4"),
)
THRESHOLDS = {
    "median_new_v4_over_pyoptix_max": 1.20,
    "every_block_new_v4_over_pyoptix_max": 1.35,
}
PRIOR_REGISTERED_GPU = {
    "name": "NVIDIA RTX A4500",
    "uuid": "GPU-5dbda20d-af85-650e-7250-10b265a77143",
    "driver": "550.127.05",
    "compute_capability": "8.6",
}
REPLICATION_SCOPES = ("same_host_temporal", "cross_gpu_reproducibility")
MACHINE_SUPPLEMENTAL_FIELDS = frozenset({
    "hostname", "platform", "python", "python_executable", "cpu_affinity",
})


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        if not isinstance(value, dict):
            raise TypeError(f"JSONL row must be an object: {path}")
        rows.append(value)
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _resolve_evidence_member(
    root: Path, relative: object, *, expected: str, ordinal: int, name: str,
) -> Path:
    require(isinstance(relative, str) and relative == expected,
            f"worker raw path differs: {ordinal}:{name}")
    member = Path(relative)
    require(not member.is_absolute() and ".." not in member.parts,
            f"worker raw path escapes evidence root: {ordinal}:{name}")
    path = (root / member).resolve(strict=True)
    require(path.is_relative_to(root) and path.is_file(),
            f"worker raw file is absent or outside evidence root: {ordinal}:{name}")
    return path


def replication_scope_matches(
    scope: object, registered_machine: object,
) -> bool:
    if scope not in REPLICATION_SCOPES or not isinstance(
            registered_machine, Mapping):
        return False
    gpu = registered_machine.get("gpu")
    if not isinstance(gpu, Mapping):
        return False
    if scope == "same_host_temporal":
        return dict(gpu) == PRIOR_REGISTERED_GPU
    return gpu.get("uuid") != PRIOR_REGISTERED_GPU["uuid"]


def expected_rows(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    unit = config["units"][UNIT_ID]
    require(unit.get("prepared_repetitions") == 3,
            "prepared repetition contract differs")
    rows = []
    for block, order in enumerate(BLOCK_ORDERS):
        for position, arm in enumerate(order):
            rows.append({
                "ordinal": len(rows),
                "unit_id": UNIT_ID,
                "endpoint": ENDPOINT,
                "block": block,
                "position": position,
                "arm": arm,
                "repetitions": 3,
                "warmups": 1,
            })
    require(len(rows) == 16, "independent schedule count differs")
    return rows


def validate_machine(
    observed: object, common: Mapping[str, Any], *, ordinal: int,
) -> None:
    registered = common.get("registered_machine")
    require(isinstance(observed, Mapping),
            f"worker machine is not an object: {ordinal}")
    require(isinstance(registered, Mapping), "registered machine is missing")
    require(set(observed) == set(registered) | MACHINE_SUPPLEMENTAL_FIELDS,
            f"worker machine fields differ: {ordinal}")
    for key, expected in registered.items():
        require(observed.get(key) == expected,
                f"worker registered machine differs: {ordinal}:{key}")
    require(observed.get("python") == common.get("python_version"),
            f"worker Python version differs: {ordinal}")
    require(observed.get("python_executable") == common.get("python_executable"),
            f"worker Python executable differs: {ordinal}")
    for key in ("hostname", "platform"):
        require(isinstance(observed.get(key), str) and bool(observed[key]),
                f"worker machine field is invalid: {ordinal}:{key}")
    affinity = common.get("cpu_affinity")
    evidence = observed.get("cpu_affinity")
    require(isinstance(affinity, Mapping) and isinstance(evidence, Mapping),
            f"worker CPU affinity is missing: {ordinal}")
    require(set(evidence) == {"preflight", "postflight"},
            f"worker CPU affinity phases differ: {ordinal}")
    require(evidence["preflight"] == affinity and evidence["postflight"] == affinity,
            f"worker CPU affinity differs: {ordinal}")


def _validate_raw_row(
    *, expected: Mapping[str, Any], observed: Mapping[str, Any], root: Path,
    config: Mapping[str, Any], config_sha256: str, worker_sha256: str,
    expected_input_digest: str, expected_output_sha256: str,
) -> Mapping[str, Any]:
    ordinal = int(expected["ordinal"])
    require(all(observed.get(key) == value for key, value in expected.items()),
            f"formal row schedule differs: {ordinal}")
    launch = observed.get("launch")
    worker = observed.get("worker")
    require(isinstance(launch, Mapping) and isinstance(worker, Mapping),
            f"formal row is incomplete: {ordinal}")
    require(launch.get("return_code") == 0 and launch.get("timeout") is False,
            f"worker launch failed: {ordinal}")
    require(launch.get("launch_error") is None,
            f"worker launch error is retained: {ordinal}")
    stem = (
        f"w{ordinal:03d}__{UNIT_ID}__{ENDPOINT}__b{expected['block']}__"
        f"p{expected['position']}__{expected['arm']}"
    )
    expected_paths = {
        "stdout": f"stdout/{stem}.bin",
        "stderr": f"stderr/{stem}.bin",
        "output": f"workers/{stem}.json",
        "journal": f"journals/{stem}.jsonl",
    }
    raw_paths = {}
    for name in ("stdout", "stderr", "output", "journal"):
        relative = launch.get(f"{name}_relative")
        path = _resolve_evidence_member(
            root, relative, expected=expected_paths[name],
            ordinal=ordinal, name=name,
        )
        require(sha256(path) == launch.get(f"{name}_sha256"),
                f"worker raw hash differs: {ordinal}:{name}")
        raw_paths[name] = path
    output_path = raw_paths["output"]
    journal_path = raw_paths["journal"]
    require(read_object(output_path) == worker,
            f"embedded worker differs from raw output: {ordinal}")
    require(worker.get("status") == "PASS",
            f"worker status differs: {ordinal}")
    require(worker.get("unit_id") == UNIT_ID
            and worker.get("arm") == expected["arm"]
            and worker.get("endpoint") == ENDPOINT,
            f"worker identity differs: {ordinal}")
    require(worker.get("formal_config_sha256") == config_sha256,
            f"worker config hash differs: {ordinal}")
    require(worker.get("formal_worker_sha256") == worker_sha256,
            f"worker executable hash differs: {ordinal}")
    require(worker.get("journal_sha256") == sha256(journal_path),
            f"worker journal identity differs: {ordinal}")
    require(worker.get("retry_count") == 0 and worker.get("discard_count") == 0,
            f"worker retry/discard differs: {ordinal}")
    require(worker.get("retained_sample_count") == 3
            and worker.get("warmup_count") == 1,
            f"worker sample population differs: {ordinal}")
    samples = worker.get("primary_samples_ns")
    require(isinstance(samples, list) and len(samples) == 3
            and all(type(value) is int and value > 0 for value in samples),
            f"worker samples are invalid: {ordinal}")
    require(worker.get("execute_samples_ns") == samples
            and worker.get("primary_median_ns") == int(statistics.median(samples)),
            f"worker sample summaries differ: {ordinal}")
    require(digest(worker.get("input_identity")) == expected_input_digest,
            f"worker input identity differs: {ordinal}")
    require(worker.get("output_sha256") == expected_output_sha256,
            f"worker output differs: {ordinal}")
    outputs = worker.get("outputs")
    require(isinstance(outputs, list) and len(outputs) == 3
            and all(isinstance(row, Mapping)
                    and row.get("matched") is True
                    and row.get("output_sha256") == expected_output_sha256
                    for row in outputs),
            f"worker retained output evidence differs: {ordinal}")
    phases = worker.get("phase_ns")
    require(isinstance(phases, Mapping)
            and set(phases) == {"load", "prepare", "close"}
            and all(type(value) is int and value > 0 for value in phases.values()),
            f"worker phase evidence differs: {ordinal}")
    require(worker.get("complete_timer_includes_prepare_execute_close") is False
            and worker.get("input_load_included_in_primary_timer") is False
            and worker.get("journal_io_included_in_primary_timer") is False,
            f"worker prepared timing boundary differs: {ordinal}")
    validate_machine(worker.get("machine"), config["common"], ordinal=ordinal)

    identity = worker.get("implementation_identity")
    registered = config["implementations"][str(expected["arm"])]
    require(isinstance(identity, Mapping),
            f"implementation identity is absent: {ordinal}")
    for key in (
        "source_root", "source_commit", "source_tree",
        "native_library_path", "native_library_sha256",
    ):
        require(identity.get(key) == registered.get(key),
                f"implementation identity differs: {ordinal}:{key}")
    require(identity.get("source_status_clean") is True,
            f"implementation checkout was dirty: {ordinal}")

    journal = read_jsonl(journal_path)
    expected_events = [
        "worker_started", "cpu_affinity_preflight", "prepared",
        "warmup_complete", "sample_complete", "sample_complete",
        "sample_complete", "close_complete", "cpu_affinity_postflight",
    ]
    require(len(journal) == len(expected_events)
            and [row.get("event") for row in journal] == expected_events
            and all(row.get("schema") == JOURNAL_SCHEMA for row in journal),
            f"worker journal order or schema differs: {ordinal}")
    require(journal[0].get("pid") == worker.get("process_id")
            and journal[0].get("arm") == expected["arm"]
            and journal[0].get("unit_id") == UNIT_ID
            and journal[0].get("endpoint") == ENDPOINT,
            f"worker journal start identity differs: {ordinal}")
    prepared = journal[2]
    warmups = [journal[3]]
    retained = journal[4:7]
    closes = [journal[7]]
    require(prepared.get("prepare_ns") == phases["prepare"],
            f"worker journal prepare phase differs: {ordinal}")
    require(warmups[0].get("index") == 0
            and warmups[0].get("output_sha256") == expected_output_sha256,
            f"worker warmup evidence differs: {ordinal}")
    require([row.get("index") for row in retained] == [0, 1, 2]
            and all(row.get("output_sha256") == expected_output_sha256
                    for row in retained),
            f"worker retained output journal differs: {ordinal}")
    require(closes[0].get("close_ns") == phases["close"],
            f"worker journal close phase differs: {ordinal}")
    require([row.get("elapsed_ns") for row in retained] == samples,
            f"worker journal samples differ: {ordinal}")
    affinity = worker["machine"]["cpu_affinity"]
    for phase in ("preflight", "postflight"):
        events = [
            row for row in journal
            if row.get("event") == f"cpu_affinity_{phase}"
        ]
        require(len(events) == 1 and events[0].get("observation") == affinity[phase],
                f"worker affinity journal differs: {ordinal}:{phase}")
    return worker


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--dry-run-summary", type=Path, required=True)
    parser.add_argument("--formal-root", type=Path, required=True)
    parser.add_argument("--controller", type=Path, required=True)
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    config_path = args.config.resolve(strict=True)
    prereg_path = args.preregistration.resolve(strict=True)
    dry_path = args.dry_run_summary.resolve(strict=True)
    root = args.formal_root.resolve(strict=True)
    controller_path = args.controller.resolve(strict=True)
    worker_path = args.worker.resolve(strict=True)
    schedule_path = root / "SCHEDULE.json"
    progress_path = root / "CONTROLLER_PROGRESS.jsonl"
    summary_path = root / "SUMMARY.json"
    config = read_object(config_path)
    prereg = read_object(prereg_path)
    dry = read_object(dry_path)
    schedule = read_object(schedule_path)
    summary = read_object(summary_path)

    require(config.get("schema") == CONFIG_SCHEMA, "config schema differs")
    require(prereg.get("schema") == PREREG_SCHEMA, "preregistration schema differs")
    require(prereg.get("status") == "FROZEN_BEFORE_REPLICATION_WORKER_ZERO",
            "preregistration status differs")
    require(prereg.get("formal_worker_zero_reached") is False,
            "preregistration is not pre-action")
    require(prereg.get("formal_result_precommitted") is False,
            "preregistration precommits a result")
    require(prereg.get("formal_config_sha256") == sha256(config_path),
            "preregistered config hash differs")
    require(prereg.get("dry_run_summary_sha256") == sha256(dry_path),
            "preregistered dry-run hash differs")
    require(prereg.get("controller_sha256") == sha256(controller_path),
            "preregistered controller hash differs")
    require(prereg.get("worker_sha256") == sha256(worker_path),
            "preregistered worker hash differs")
    require(prereg.get("engineering_thresholds") == THRESHOLDS,
            "preregistered thresholds differ")
    require(prereg.get("retry_allowed") is False
            and prereg.get("discard_allowed") is False,
            "preregistration permits retry or discard")
    prior = prereg.get("prior_transaction")
    require(isinstance(prior, Mapping)
            and prior.get("pooled_into_this_replication") is False
            and prior.get("registered_gpu") == PRIOR_REGISTERED_GPU,
            "prior transaction pooling or GPU boundary differs")
    require(replication_scope_matches(
        prereg.get("replication_scope"),
        config["common"].get("registered_machine"),
    ), "declared replication scope differs from registered GPU")
    require(prereg.get("formal_worker_count") == 16
            and prereg.get("unit_id") == UNIT_ID
            and prereg.get("endpoint") == ENDPOINT
            and prereg.get("arms") == list(ARMS)
            and prereg.get("paired_blocks") == 8,
            "preregistered population differs")
    require(prereg.get("block_orders") == [list(row) for row in BLOCK_ORDERS]
            and prereg.get("prepared_repetitions_per_worker") == 3
            and prereg.get("prepared_warmups_per_worker") == 1,
            "preregistered schedule parameters differ")
    require(prereg.get("registered_machine") == config["common"].get(
        "registered_machine")
        and prereg.get("cpu_affinity") == config["common"].get("cpu_affinity")
        and prereg.get("unit") == config["units"].get(UNIT_ID),
        "preregistered machine or unit differs")
    require(prereg.get("implementations") == {
        arm: config["implementations"][arm] for arm in ARMS
    }, "preregistered implementation identities differ")
    require(prereg.get("input_identity_sha256")
            == digest(prereg.get("input_identity")),
            "preregistered input identity digest differs")
    require(dry.get("schema") == SUMMARY_SCHEMA
            and dry.get("status") == "COMPLETE__DRY_RUN_PARITY_PASS"
            and dry.get("worker_count") == 2
            and dry.get("config_sha256") == sha256(config_path)
            and dry.get("controller_sha256") == sha256(controller_path)
            and dry.get("worker_sha256") == sha256(worker_path)
            and dry.get("retry_count") == 0
            and dry.get("discard_count") == 0,
            "dry-run authority differs")
    dry_rows = dry.get("rows")
    require(isinstance(dry_rows, list) and len(dry_rows) == 2,
            "dry-run worker population differs")
    for row in dry_rows:
        worker = row.get("worker")
        require(isinstance(worker, Mapping), "dry-run worker is incomplete")
        require(digest(worker.get("input_identity"))
                == prereg.get("input_identity_sha256"),
                "dry-run input identity differs from preregistration")
        require(worker.get("output_sha256")
                == prereg.get("expected_output_sha256"),
                "dry-run output differs from preregistration")

    expected = expected_rows(config)
    require(schedule.get("schema") == SCHEDULE_SCHEMA
            and schedule.get("mode") == "formal",
            "formal schedule header differs")
    require(schedule.get("rows") == expected and schedule.get("worker_count") == 16,
            "formal schedule rows differ")
    require(schedule.get("config_sha256") == sha256(config_path),
            "formal schedule config hash differs")
    require(schedule.get("controller_sha256") == sha256(controller_path)
            and schedule.get("worker_sha256") == sha256(worker_path),
            "formal schedule executable hashes differ")
    require(prereg.get("formal_schedule_sha256") == digest(schedule),
            "preregistered formal schedule digest differs")
    require(summary.get("schema") == SUMMARY_SCHEMA
            and summary.get("mode") == "formal",
            "formal summary header differs")
    require(summary.get("formal_worker_zero_reached") is True
            and summary.get("config_sha256") == sha256(config_path)
            and summary.get("controller_sha256") == sha256(controller_path)
            and summary.get("worker_sha256") == sha256(worker_path),
            "formal summary identity differs")
    require(summary.get("schedule_file_sha256") == sha256(schedule_path),
            "formal summary schedule hash differs")
    require(summary.get("progress_file_sha256") == sha256(progress_path),
            "formal summary progress hash differs")
    require(summary.get("retry_count") == 0 and summary.get("discard_count") == 0,
            "formal summary retry/discard differs")

    progress = read_jsonl(progress_path)
    require(len(progress) == 17 and progress[0].get("event") == "schedule_frozen",
            "controller progress population differs")
    require(progress[0].get("formal_worker_zero_reached") is False,
            "controller progress pre-action marker differs")
    require(progress[0].get("worker_count") == 16
            and progress[0].get("schedule_sha256") == sha256(schedule_path),
            "controller progress schedule identity differs")
    require([row.get("ordinal") for row in progress[1:]] == list(range(16)),
            "controller progress worker order differs")

    observed_rows = summary.get("rows")
    require(isinstance(observed_rows, list) and len(observed_rows) == 16,
            "formal summary worker population differs")
    input_digest = str(prereg["input_identity_sha256"])
    output_sha = str(prereg["expected_output_sha256"])
    workers: dict[tuple[int, str], Mapping[str, Any]] = {}
    process_ids = set()
    for expected, observed in zip(expected, observed_rows, strict=True):
        worker = _validate_raw_row(
            expected=expected,
            observed=observed,
            root=root,
            config=config,
            config_sha256=sha256(config_path),
            worker_sha256=sha256(worker_path),
            expected_input_digest=input_digest,
            expected_output_sha256=output_sha,
        )
        pid = worker.get("process_id")
        require(type(pid) is int and pid > 0 and pid not in process_ids,
                f"worker PID is invalid or reused: {expected['ordinal']}")
        process_ids.add(pid)
        workers[(int(expected["block"]), str(expected["arm"]))] = worker
        progress_row = progress[int(expected["ordinal"]) + 1]
        launch = observed["launch"]
        require(progress_row.get("event") == "worker_complete"
                and progress_row.get("unit_id") == UNIT_ID
                and progress_row.get("arm") == expected["arm"]
                and progress_row.get("endpoint") == ENDPOINT
                and progress_row.get("return_code") == 0
                and progress_row.get("timeout") is False
                and progress_row.get("output_sha256")
                    == launch.get("output_sha256")
                and progress_row.get("journal_sha256")
                    == launch.get("journal_sha256"),
                f"controller progress worker record differs: {expected['ordinal']}")

    block_rows = []
    ratios = []
    for block in range(8):
        by_arm = {arm: workers[(block, arm)] for arm in ARMS}
        medians = {
            arm: int(statistics.median(by_arm[arm]["primary_samples_ns"]))
            for arm in ARMS
        }
        ratio = medians["new_v4"] / medians["pyoptix"]
        ratios.append(ratio)
        block_rows.append({
            "block": block,
            "medians_ns": medians,
            "new_v4_over_pyoptix": ratio,
        })
    median_ratio = statistics.median(ratios)
    maximum_ratio = max(ratios)
    target_met = (
        median_ratio <= THRESHOLDS["median_new_v4_over_pyoptix_max"]
        and maximum_ratio <= THRESHOLDS["every_block_new_v4_over_pyoptix_max"]
    )
    expected_status = "COMPLETE__REPLICATION_TARGET_MET" if target_met \
        else "COMPLETE__REPLICATION_TARGET_NOT_MET"
    require(summary.get("status") == expected_status,
            "formal summary status differs from independent result")
    require(summary.get("worker_count") == 16
            and summary.get("valid_block_count") == 8
            and summary.get("registered_block_count") == 8
            and summary.get("method_complete") is True
            and summary.get("engineering_target_met") is target_met,
            "formal summary population or verdict differs")
    require(summary.get("median_new_v4_over_pyoptix") == median_ratio
            and summary.get("max_new_v4_over_pyoptix") == maximum_ratio,
            "formal summary statistics differ")
    expected_cells = [{
        "unit_id": UNIT_ID,
        "endpoint": ENDPOINT,
        "block": row["block"],
        "valid": True,
        "reason": None,
        "medians_ns": row["medians_ns"],
        "new_v4_over_pyoptix": row["new_v4_over_pyoptix"],
    } for row in block_rows]
    require(summary.get("cells") == expected_cells,
            "formal summary cells differ from independent reconstruction")

    payload = {
        "schema": "rtdl.v4_long_workload.replication_recount.v1",
        "status": "PASS__METHOD_AND_TARGET" if target_met
        else "PASS__METHOD__ENGINEERING_TARGET_NOT_MET",
        "project_modules_imported": False,
        "formal_worker_count": 16,
        "distinct_process_id_count": len(process_ids),
        "formal_cell_count": 8,
        "retry_count": 0,
        "discard_count": 0,
        "all_raw_file_hashes_verified": True,
        "all_journals_reconstructed": True,
        "all_input_and_output_identities_verified": True,
        "prior_transaction_pooled": False,
        "replication_scope": prereg["replication_scope"],
        "block_results": block_rows,
        "median_new_v4_over_pyoptix": median_ratio,
        "max_new_v4_over_pyoptix": maximum_ratio,
        "engineering_target_met": target_met,
        "identities": {
            "config_sha256": sha256(config_path),
            "preregistration_sha256": sha256(prereg_path),
            "dry_run_summary_sha256": sha256(dry_path),
            "controller_sha256": sha256(controller_path),
            "worker_sha256": sha256(worker_path),
            "formal_schedule_sha256": sha256(schedule_path),
            "formal_progress_sha256": sha256(progress_path),
            "formal_summary_sha256": sha256(summary_path),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({
        "status": payload["status"],
        "output": str(args.output),
        "median_new_v4_over_pyoptix": median_ratio,
        "max_new_v4_over_pyoptix": maximum_ratio,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
