#!/usr/bin/env python3
"""Export the frozen two-generation evidence into a portable anonymous package."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import tarfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
M_COMMIT = "d653fe4ad170c5b51fee309d653c9565944dcf2e"
M_TREE = "d53af23a2599f9d6adb4ac0bfff39cd0ab31860b"
E_COMMIT = "12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8"
E_TREE = "aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6"
CROSS_AUTHORITY_SHA256 = "99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692"
ARCHIVE_PREFIX = "rtdl-cgo2027-artifact"

EXPECTED_GENERATIONS = {
    "G0_ADA": {
        "argument": "ada_root",
        "architecture": "Ada",
        "compute_capability": "8.9",
        "manifest_file_sha256": "e71f98c713ee9c7c0bb5733d5ff1921d11eea5bc819ec3fea217961f9a690f6f",
        "manifest_self_seal": "8cbd609118b3b2c634a1a3dbec4c10ebd585fc527452083ae6f7ba650222fe06",
        "authority_sha256": "191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7",
        "transaction_file_sha256": "7fea3656ae8724b2219dbd08866aeb9b6215a8b6090b72b125defbdc38498ab6",
        "instrumentation_authority_file_sha256": "0add50de314ea3025eba3de3ac0187d34b066f211d6d5c469da06540011dcd4f",
        "aot_authority_file_sha256": "e76dac08921882dfc4257d5ce2d6d19dc2e9fce67df511440fb7a33481efe404",
        "competence_authority_file_sha256": "d6e9ec1bfced0b7a1a5527e9f00ea0e3bf526c97c70483f59ec1cdaf970d5308",
        "archive_name": "goal5848-ada89-rtx4090-d653fe4-transaction4-20260906.tar.gz",
        "archive_sha256": "c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced",
    },
    "G1_AMPERE": {
        "argument": "ampere_root",
        "architecture": "Ampere",
        "compute_capability": "8.6",
        "manifest_file_sha256": "9f1031c4fc07bf23635904f7f93e075a0a3c1a0ed5aaa21f6dc48e47d92b9340",
        "manifest_self_seal": "c0ff8626df78ac7039b3182de8e025d7d5ac440e1a135d9cb0235a9dffa7c240",
        "authority_sha256": "35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3",
        "transaction_file_sha256": "b84ad3103809c1c2cf40c1ab3401e4d48d0fd11509f75548efefd78e1cc791e5",
        "instrumentation_authority_file_sha256": "4de72215ac9c0e7891175e6e6b65fc3bec6eaa047580952f7ef6f38c74126f48",
        "aot_authority_file_sha256": "7114c61cf3601acf1e58b2121bf83db4d7893f144a0d7204f28b94c32cbb65a7",
        "competence_authority_file_sha256": "34b2066b0557a876e6475cddc746b5decb4c4429f35203ec2ac634158270943e",
        "archive_name": "goal5848-ampere86-d653fe4-transaction2.tar.gz",
        "archive_sha256": "7bbabfc8d1d9dfd3cc9bd701bd7f40e9f50c8ccfcbbac9504db43e9e42b7c2a2",
    },
}


class ExportError(ValueError):
    """The source evidence or requested output violates the frozen contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExportError(message)


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def strict_json(path: Path) -> object:
    def object_from_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ExportError(f"{path}: duplicate JSON key {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise ExportError(f"{path}: non-finite JSON value {value}")

    try:
        return json.loads(
            path.read_bytes(),
            object_pairs_hook=object_from_pairs,
            parse_constant=reject_constant,
        )
    except ExportError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ExportError(f"{path}: not readable strict JSON") from error


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode("utf-8")
        + b"\n"
    )


def _load_verifier(template_root: Path):
    path = template_root / "verify.py"
    require(path.is_file() and not path.is_symlink(), "template verifier is absent")
    spec = importlib.util.spec_from_file_location("goal5852_artifact_verify", path)
    require(spec is not None and spec.loader is not None, "cannot load template verifier")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def _load_contracts():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from experiments.goal5848_strong_baseline import contracts

    return contracts


def _validate_seal(value: Mapping[str, object], field: str, label: str) -> None:
    body = dict(value)
    seal = body.pop(field, None)
    require(type(seal) is str and len(seal) == 64, f"{label}: seal is absent")
    require(seal == digest(body), f"{label}: seal differs")


def _validate_input_manifest(root: Path, expected: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    manifest_path = root / "EVIDENCE_MANIFEST.json"
    require(manifest_path.is_file() and not manifest_path.is_symlink(), f"{root}: manifest absent")
    require(sha256_file(manifest_path) == expected["manifest_file_sha256"], f"{root}: manifest file identity differs")
    manifest = strict_json(manifest_path)
    require(isinstance(manifest, Mapping), f"{root}: manifest must be an object")
    body = dict(manifest)
    seal = body.pop("manifest_sha256", None)
    require(seal == expected["manifest_self_seal"] == digest(body), f"{root}: manifest self-seal differs")
    require(manifest.get("schema") == "rtdl.goal5848.evidence_manifest.v1", f"{root}: manifest schema differs")
    require(manifest.get("status") == "PASS__ONE_GENERATION_COMPLETE_EVIDENCE_FILE_SET", f"{root}: manifest status differs")
    require(manifest.get("file_count") == 2405, f"{root}: manifest member count differs")
    require(manifest.get("discard_count") == 0 and manifest.get("retry_count") == 0, f"{root}: manifest retry/discard differs")
    rows = manifest.get("rows")
    require(isinstance(rows, list) and len(rows) == 2405, f"{root}: manifest rows differ")
    indexed: dict[str, Mapping[str, object]] = {}
    total = 0
    for position, row in enumerate(rows):
        require(isinstance(row, Mapping) and set(row) == {"bytes", "path", "sha256"}, f"{root}: manifest row {position} differs")
        relative = PurePosixPath(row["path"])
        require(not relative.is_absolute() and ".." not in relative.parts, f"{root}: unsafe manifest path")
        name = relative.as_posix()
        require(name not in indexed, f"{root}: duplicate manifest path {name}")
        path = root.joinpath(*relative.parts)
        require(path.is_file() and not path.is_symlink(), f"{root}: missing or symlinked member {name}")
        require(type(row["bytes"]) is int and row["bytes"] >= 0, f"{root}: invalid member bytes {name}")
        require(path.stat().st_size == row["bytes"], f"{root}: member byte count differs {name}")
        require(sha256_file(path) == row["sha256"], f"{root}: member hash differs {name}")
        total += row["bytes"]
        indexed[name] = row
    require(total == manifest.get("payload_bytes"), f"{root}: payload byte total differs")
    archive_name = str(expected["archive_name"])
    allowed_extra = {"EVIDENCE_MANIFEST.json", archive_name, archive_name + ".sha256"}
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    require(actual == set(indexed) | allowed_extra, f"{root}: unexpected or missing raw member")
    archive = root / archive_name
    require(archive.is_file() and not archive.is_symlink(), f"{root}: archive absent")
    require(sha256_file(archive) == expected["archive_sha256"], f"{root}: archive identity differs")
    sidecar = (root / (archive_name + ".sha256")).read_text(encoding="utf-8").strip().split()
    require(bool(sidecar) and sidecar[0] == expected["archive_sha256"], f"{root}: archive sidecar digest differs")
    authority = root / "single-generation-authority.json"
    recount = root / "single-generation-authority.recount.json"
    require(authority.read_bytes() == recount.read_bytes(), f"{root}: authority/recount bytes differ")
    require(sha256_file(authority) == expected["authority_sha256"], f"{root}: authority identity differs")
    exact_files = {
        "formal-transaction/transaction.json": "transaction_file_sha256",
        "instrumentation-overhead/authority.json": "instrumentation_authority_file_sha256",
        "aot-hit/authority.json": "aot_authority_file_sha256",
        "baseline-competence/authority.json": "competence_authority_file_sha256",
    }
    for relative, expected_key in exact_files.items():
        require(sha256_file(root / relative) == expected[expected_key], f"{root}: exact authority differs {relative}")
    return indexed


def _validate_process_binding(root: Path, worker: Mapping[str, object], worker_id: str) -> dict[str, str]:
    path = root / "formal-transaction" / "processes" / f"{worker_id}.json"
    process = strict_json(path)
    require(isinstance(process, Mapping), f"{worker_id}: process receipt absent")
    _validate_seal(process, "process_sha256", f"{worker_id}: process")
    require(process.get("schema") == "rtdl.goal5848.formal_process.v2", f"{worker_id}: process schema differs")
    require(process.get("exit_code") == 0, f"{worker_id}: process failed")
    stdout = process.get("stdout_utf8")
    stderr = process.get("stderr_utf8")
    require(type(stdout) is str and type(stderr) is str, f"{worker_id}: process streams absent")
    require(hashlib.sha256(stdout.encode()).hexdigest() == process.get("stdout_sha256"), f"{worker_id}: stdout digest differs")
    require(hashlib.sha256(stderr.encode()).hexdigest() == process.get("stderr_sha256"), f"{worker_id}: stderr digest differs")
    try:
        stdout_value = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise ExportError(f"{worker_id}: stdout is not worker JSON") from error
    require(stdout_value == worker, f"{worker_id}: stdout/worker binding differs")
    return {
        "process_file_sha256": sha256_file(path),
        "process_receipt_sha256": str(process["process_sha256"]),
    }


def _seal_row(value: dict[str, object]) -> dict[str, object]:
    return {**value, "row_sha256": digest(value)}


def _project_formal(
    root: Path,
    generation: str,
    expected: Mapping[str, object],
    contracts,
    verifier,
) -> tuple[list[dict[str, object]], list[dict[str, object]], Mapping[str, object]]:
    transaction = strict_json(root / "formal-transaction" / "transaction.json")
    require(isinstance(transaction, Mapping), f"{generation}: transaction absent")
    require(transaction.get("expected_source_commit") == M_COMMIT, f"{generation}: transaction M differs")
    require(transaction.get("expected_predecessor_commit") == E_COMMIT, f"{generation}: transaction E differs")
    require(transaction.get("worker_count") == 80 and transaction.get("process_count") == 80, f"{generation}: transaction population differs")
    schedule = contracts.build_schedule()
    worker_dir = root / "formal-transaction" / "workers"
    actual = {path.name for path in worker_dir.glob("*.json")}
    expected_names = {f"{row['worker_id']}.json" for row in schedule}
    require(actual == expected_names, f"{generation}: formal worker member set differs")
    projected = []
    provenance = []
    hardware: Mapping[str, object] | None = None
    for schedule_row in schedule:
        worker_id = str(schedule_row["worker_id"])
        path = worker_dir / f"{worker_id}.json"
        value = strict_json(path)
        require(isinstance(value, Mapping), f"{worker_id}: worker absent")
        worker = contracts.validate_worker_receipt(
            value,
            expected_row=schedule_row,
            expected_source_commit=M_COMMIT,
            expected_predecessor_commit=E_COMMIT,
        )
        if hardware is None:
            hardware = worker["hardware"]
        require(worker["hardware"] == hardware, f"{generation}: mixed worker hardware")
        require(hardware["compute_capability"] == expected["compute_capability"], f"{generation}: compute capability differs")
        process_binding = _validate_process_binding(root, worker, worker_id)
        measurements = worker["measurements"]
        evidence = measurements["evidence"]
        arm = str(worker["arm"])
        public_arm = verifier.ARMS[contracts.ARMS.index(arm)]
        task = str(worker["task"])
        block = int(worker["block"])
        steady = measurements["steady_complete_execution"]
        samples = list(steady["samples_ns"])
        lifecycle = None
        if arm != contracts.DIRECT_OPTIX_ARM:
            lifecycle = {
                "component_diagnostics_ns": dict(measurements["component_diagnostics_ns"]),
                "endpoint_partition_ns": dict(measurements["endpoint_partition_ns"]),
                "implementation_entry_to_first_correct_result_ns": measurements["implementation_entry_to_first_correct_result_ns"],
                "implementation_import_ns": measurements["implementation_import_ns"],
                "implementation_import_to_endpoint_gap_ns": measurements["implementation_import_to_endpoint_gap_ns"],
                "post_import_to_first_correct_result_ns": measurements["post_import_to_first_correct_result_ns"],
            }
        cell_id = f"{generation}-B{block:02d}-T{contracts.TASKS.index(task)}-A{contracts.ARMS.index(arm)}"
        row = _seal_row({
            "arm": public_arm,
            "block": block,
            "cell_id": cell_id,
            "generation": generation,
            "lifecycle": lifecycle,
            "oracle_exact": True,
            "output_sha256": evidence["output_sha256"],
            "phase_instrumentation": None if arm == contracts.DIRECT_OPTIX_ARM else evidence.get("phase_instrumentation"),
            "source_label": "E_FROZEN_PREDECESSOR" if arm == contracts.PREDECESSOR_RTDL_ARM else "M_MEASURED_SUCCESSOR",
            "steady_median_ns": steady["median_ns"],
            "steady_samples_ns": samples,
            "steady_samples_sha256": digest(samples),
            "task": task,
        })
        projected.append(row)
        provenance.append({
            "projection_cell_id": cell_id,
            "raw_relative_path": path.relative_to(root).as_posix(),
            "raw_file_sha256": sha256_file(path),
            "raw_worker_receipt_sha256": worker["result_sha256"],
            **process_binding,
        })
    require(hardware is not None, f"{generation}: no formal hardware")
    return projected, provenance, hardware


def _project_instrumentation(root: Path, generation: str, hardware: Mapping[str, object], contracts) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    worker_dir = root / "instrumentation-overhead" / "workers"
    actual = {path.name for path in worker_dir.glob("*.json")}
    expected_names = set()
    projected = []
    provenance = []
    for replicate in range(16):
        for block in range(8):
            for task in contracts.TASKS:
                for mode in ("off", "on"):
                    worker_id = f"G5848_INSTRUMENTATION_R{replicate:02d}_B{block:02d}_{task}_{mode.upper()}"
                    expected_names.add(worker_id + ".json")
                    path = worker_dir / f"{worker_id}.json"
                    value = strict_json(path)
                    require(isinstance(value, Mapping), f"{worker_id}: worker absent")
                    _validate_seal(value, "result_sha256", worker_id)
                    measurements = value.get("measurements")
                    source = value.get("source")
                    require(value.get("schema") == contracts.WORKER_SCHEMA and value.get("status") == "PASS__GOAL5848_WORKER", f"{worker_id}: worker status differs")
                    require(value.get("arm") == contracts.RTDL_ARM and value.get("task") == task and value.get("block") == block, f"{worker_id}: schedule binding differs")
                    require(value.get("classification") == "exploration" and value.get("warmups") == 1 and value.get("repetitions") == 1, f"{worker_id}: instrumentation contract differs")
                    require(value.get("hardware") == hardware, f"{worker_id}: hardware differs")
                    require(source == {"clean": True, "commit": M_COMMIT, "status": "", "tree": M_TREE}, f"{worker_id}: source differs")
                    require(isinstance(measurements, Mapping), f"{worker_id}: measurements absent")
                    entry = measurements.get("implementation_entry_to_first_correct_result_ns")
                    import_ns = measurements.get("implementation_import_ns")
                    gap_ns = measurements.get("implementation_import_to_endpoint_gap_ns")
                    post_ns = measurements.get("post_import_to_first_correct_result_ns")
                    require(all(type(item) is int for item in (entry, import_ns, gap_ns, post_ns)), f"{worker_id}: endpoint types differ")
                    require(entry == import_ns + gap_ns + post_ns and entry > 0 and import_ns > 0 and gap_ns >= 0 and post_ns > 0, f"{worker_id}: endpoint does not reconcile")
                    evidence = measurements.get("evidence")
                    require(isinstance(evidence, Mapping) and evidence.get("phase_instrumentation") is (mode == "on"), f"{worker_id}: instrumentation mode differs")
                    require(evidence.get("output_sha256") == contracts.TASK_CONTRACTS[task]["public_output_sha256"], f"{worker_id}: output digest differs")
                    steady = measurements.get("steady_complete_execution")
                    require(isinstance(steady, Mapping) and steady.get("samples_ns") and len(steady["samples_ns"]) == 1, f"{worker_id}: one-sample receipt differs")
                    projected.append(_seal_row({
                        "block": block,
                        "endpoint_ns": entry,
                        "generation": generation,
                        "mode": mode,
                        "replicate": replicate,
                        "source_label": "M_MEASURED_SUCCESSOR",
                        "task": task,
                    }))
                    provenance.append({
                        "projection_instrumentation_key": f"{generation}/{task}/{block}/{mode}/{replicate}",
                        "raw_relative_path": path.relative_to(root).as_posix(),
                        "raw_file_sha256": sha256_file(path),
                        "raw_worker_receipt_sha256": value["result_sha256"],
                    })
    require(actual == expected_names, f"{generation}: instrumentation worker member set differs")
    return projected, provenance


def _project_aot(root: Path, generation: str, contracts) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    authority = strict_json(root / "aot-hit" / "authority.json")
    require(isinstance(authority, Mapping) and authority.get("worker_count") == 10, f"{generation}: AOT authority differs")
    require(authority.get("source_commit") == M_COMMIT, f"{generation}: AOT source differs")
    grouped: dict[str, list[int]] = {task: [] for task in contracts.TASKS}
    provenance = []
    pids = set()
    files = sorted(path for path in (root / "aot-hit").glob("*.json") if path.name != "authority.json")
    require(len(files) == 10, f"{generation}: AOT worker member count differs")
    for path in files:
        value = strict_json(path)
        require(isinstance(value, Mapping), f"{path}: AOT worker absent")
        _validate_seal(value, "receipt_sha256", str(path))
        task = value.get("task")
        require(task in contracts.TASKS, f"{path}: AOT task differs")
        duration = value.get("duration_ns")
        require(type(duration) is int and duration > 0, f"{path}: AOT duration differs")
        require(value.get("source_commit") == M_COMMIT, f"{path}: AOT source differs")
        require(value.get("cache_hit") is True and value.get("producer_invoked") is False and value.get("producer_call_count") == 0, f"{path}: AOT hit contract differs")
        require(value.get("compiler_modules_before") == value.get("compiler_modules_after") == [], f"{path}: compiler modules present")
        require(value.get("nvrtc_mappings_before") == value.get("nvrtc_mappings_after") == [], f"{path}: NVRTC mapping present")
        require(type(value.get("pid")) is int and value["pid"] not in pids, f"{path}: AOT PID differs")
        pids.add(value["pid"])
        grouped[task].append(duration)
        provenance.append({
            "projection_aot_key": f"{generation}/{task}/{len(grouped[task]) - 1}",
            "raw_relative_path": path.relative_to(root).as_posix(),
            "raw_file_sha256": sha256_file(path),
            "raw_worker_receipt_sha256": value["receipt_sha256"],
        })
    projected = []
    for task in contracts.TASKS:
        task_authority = authority.get("tasks", {}).get(task)
        require(isinstance(task_authority, Mapping), f"{generation}/{task}: AOT authority row absent")
        durations = grouped[task]
        require(durations == task_authority.get("fresh_process_hit_durations_ns"), f"{generation}/{task}: AOT duration authority differs")
        projected.append(_seal_row({
            "cold_first_resolution_ns": task_authority["cold_first_resolution_ns"],
            "durations_ns": durations,
            "generation": generation,
            "source_label": "M_MEASURED_SUCCESSOR",
            "task": task,
        }))
    return projected, provenance


def _project_competence(root: Path, generation: str, hardware: Mapping[str, object], contracts) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    worker_dir = root / "baseline-competence" / "workers"
    files = sorted(worker_dir.glob("*.json"))
    require(len(files) == 4, f"{generation}: competence worker count differs")
    projected = []
    provenance = []
    seen = set()
    for path in files:
        value = strict_json(path)
        require(isinstance(value, Mapping), f"{path}: competence worker absent")
        _validate_seal(value, "result_sha256", str(path))
        arm = value.get("arm")
        task = value.get("task")
        require(arm in (contracts.IDIOMATIC_PYOPTIX_ARM, contracts.STRONG_PYOPTIX_ARM) and task in contracts.TASKS, f"{path}: competence identity differs")
        require((task, arm) not in seen, f"{path}: duplicate competence cell")
        seen.add((task, arm))
        require(value.get("classification") == "exploration" and value.get("warmups") == 16 and value.get("repetitions") == 128, f"{path}: competence contract differs")
        require(value.get("hardware") == hardware, f"{path}: competence hardware differs")
        require(value.get("source") == {"clean": True, "commit": M_COMMIT, "status": "", "tree": M_TREE}, f"{path}: competence source differs")
        measurements = value.get("measurements")
        require(isinstance(measurements, Mapping), f"{path}: competence measurements absent")
        steady = measurements.get("steady_complete_execution")
        require(isinstance(steady, Mapping), f"{path}: competence steady receipt absent")
        samples = steady.get("samples_ns")
        require(isinstance(samples, list) and len(samples) == 128 and all(type(item) is int and item > 0 for item in samples), f"{path}: competence samples differ")
        require(steady.get("median_ns") == contracts.integer_median(samples), f"{path}: competence median differs")
        evidence = measurements.get("evidence")
        require(isinstance(evidence, Mapping) and evidence.get("output_sha256") == contracts.TASK_CONTRACTS[task]["public_output_sha256"], f"{path}: competence output differs")
        projected.append(_seal_row({
            "arm": arm,
            "generation": generation,
            "source_label": "M_MEASURED_SUCCESSOR",
            "steady_median_ns": steady["median_ns"],
            "steady_samples_ns": samples,
            "steady_samples_sha256": digest(samples),
            "task": task,
        }))
        provenance.append({
            "projection_competence_key": f"{generation}/{task}/{arm}",
            "raw_relative_path": path.relative_to(root).as_posix(),
            "raw_file_sha256": sha256_file(path),
            "raw_worker_receipt_sha256": value["result_sha256"],
        })
    require(len(seen) == 4, f"{generation}: competence schedule incomplete")
    return projected, provenance


def collect_projection(
    *,
    ada_root: Path,
    ampere_root: Path,
    cross_root: Path,
    template_root: Path,
) -> tuple[dict[str, object], dict[str, object], object]:
    verifier = _load_verifier(template_root)
    contracts = _load_contracts()
    roots = {
        "G0_ADA": ada_root.resolve(),
        "G1_AMPERE": ampere_root.resolve(),
    }
    formal_rows = []
    instrumentation_rows = []
    aot_rows = []
    competence_rows = []
    generation_provenance = []
    for generation in verifier.GENERATIONS:
        root = roots[generation]
        expected = EXPECTED_GENERATIONS[generation]
        manifest_index = _validate_input_manifest(root, expected)
        formal, formal_provenance, hardware = _project_formal(
            root, generation, expected, contracts, verifier
        )
        instrumentation, instrumentation_provenance = _project_instrumentation(root, generation, hardware, contracts)
        aot, aot_provenance = _project_aot(root, generation, contracts)
        competence, competence_provenance = _project_competence(root, generation, hardware, contracts)
        formal_rows.extend(formal)
        instrumentation_rows.extend(instrumentation)
        aot_rows.extend(aot)
        competence_rows.extend(competence)
        generation_provenance.append({
            "generation_label": generation,
            "raw_root": str(root),
            "raw_manifest_file_sha256": expected["manifest_file_sha256"],
            "raw_manifest_self_seal": expected["manifest_self_seal"],
            "raw_manifest_member_count": len(manifest_index),
            "single_generation_authority_sha256": expected["authority_sha256"],
            "archive_sha256": expected["archive_sha256"],
            "private_hardware_identity": dict(hardware),
            "formal_map": formal_provenance,
            "instrumentation_map": instrumentation_provenance,
            "aot_map": aot_provenance,
            "competence_map": competence_provenance,
        })
    cross_root = cross_root.resolve()
    cross_authority = cross_root / "goal5848-cross-generation-authority.json"
    cross_recount = cross_root / "goal5848-cross-generation-authority.recount.json"
    require(
        {path.name for path in cross_root.iterdir()} == {cross_authority.name, cross_recount.name},
        "cross-generation root member set differs",
    )
    require(cross_authority.read_bytes() == cross_recount.read_bytes(), "cross authority/recount bytes differ")
    require(sha256_file(cross_authority) == CROSS_AUTHORITY_SHA256, "cross authority identity differs")
    formal_rows.sort(key=lambda row: (verifier.GENERATIONS.index(row["generation"]), row["block"], verifier.TASKS.index(row["task"]), verifier.ARMS.index(row["arm"])))
    instrumentation_rows.sort(key=lambda row: (verifier.GENERATIONS.index(row["generation"]), verifier.TASKS.index(row["task"]), row["block"], row["mode"], row["replicate"]))
    aot_rows.sort(key=lambda row: (verifier.GENERATIONS.index(row["generation"]), verifier.TASKS.index(row["task"])))
    competence_rows.sort(key=lambda row: (verifier.GENERATIONS.index(row["generation"]), verifier.TASKS.index(row["task"]), verifier.ARMS.index(row["arm"])))
    body = {
        "schema": verifier.PROJECTION_SCHEMA,
        "contract": verifier.EXPECTED_CONTRACT,
        "formal_workers": formal_rows,
        "instrumentation_workers": instrumentation_rows,
        "aot_qualification": aot_rows,
        "nonformal_competence_workers": competence_rows,
        "claim_boundary": {
            "cross_machine_raw_time_ratio_computed": False,
            "external_review_complete": False,
            "offline_recount_is_gpu_execution": False,
            "original_per_execution_receipt_requirement_fulfilled": False,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    projection = {**body, "projection_sha256": digest(body)}
    provenance_body = {
        "schema": "rtdl.cgo2027.submission_evidence.private_provenance.v1",
        "measured_successor_commit": M_COMMIT,
        "measured_successor_tree": M_TREE,
        "predecessor_commit": E_COMMIT,
        "predecessor_tree": E_TREE,
        "cross_root": str(cross_root),
        "cross_authority_sha256": CROSS_AUTHORITY_SHA256,
        "projection_sha256": projection["projection_sha256"],
        "generation_inputs": generation_provenance,
        "anonymization_rules": {
            "removed": ["raw paths", "GPU UUIDs", "driver versions", "user names", "process commands", "host environment"],
            "replaced": ["GPU identity -> architecture generation label", "source commit -> M/E source label", "worker ID -> anonymous schedule cell"],
            "unchanged": ["all 20480 formal ns samples", "all lifecycle duration fields", "all thresholds and gate types", "all task/arm/block assignments", "all A-only instrumentation endpoints", "all AOT durations", "all competence samples"],
        },
        "claim_boundary": {
            "private_provenance_is_public_package_member": False,
            "projection_is_raw_archive_byte_identity": False,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    provenance = {**provenance_body, "provenance_sha256": digest(provenance_body)}
    return projection, provenance, verifier


def _format_ratio(ppm: int) -> str:
    return f"{ppm / 1_000_000:.6f}x"


def _public_documents(summary: Mapping[str, object]) -> dict[str, bytes]:
    rows = summary["performance_rows"]
    table_lines = [
        "| Generation | Task | A/D prepared median | A/D observed max | A/C entry median | A/C post-import median |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    ae_lines = [
        "| Generation | Task | A/E prepared median | A/E post-import | A/E entry |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        table_lines.append(
            f"| {row['generation']} | {row['task']} | {_format_ratio(row['a_over_d_steady_median_ppm'])} | {_format_ratio(row['a_over_d_steady_max_ppm'])} | {_format_ratio(row['a_over_c_entry_median_ppm'])} | {_format_ratio(row['a_over_c_post_import_median_ppm'])} |"
        )
        ae_lines.append(
            f"| {row['generation']} | {row['task']} | {_format_ratio(row['a_over_e_steady_median_ppm'])} | {_format_ratio(row['a_over_e_post_import_median_ppm'])} | {_format_ratio(row['a_over_e_entry_median_ppm'])} |"
        )
    values = {
        "README.md": """# Anonymous RTDL evidence projection

This package supports a standard-library-only offline recount of a frozen
two-generation performance projection. It does not run a GPU or install RTDL.

Quick start from the extracted package root:

```sh
python3 verify.py --artifact-root .
```

The verifier checks the exact member set and hashes, reconstructs 160 formal
worker medians from 20,480 retained nanosecond samples, recomputes all reported
ratios, and rejects changes to the frozen projection.
""",
        "EXPECTED_RESULTS.md": "# Expected offline reconstruction\n\n" + "\n".join(table_lines) + "\n\nThe A/D maximum is descriptive; no A/D worst-block gate exists.\n\n" + "\n".join(ae_lines) + "\n\nA/E post-import and entry are post hoc, non-gating diagnostics. The largest A/C post-import diagnostic block is 2.377129x.\n",
        "CLAIM_SCOPE.md": """# Claim scope

The package preserves a narrow observation of the exact prepared public path
on two frozen tasks and two GPU generations. Ratios are computed only within a
machine. They are not intrinsic language speedups or universal parity claims.

Native and compact-status failures are rejected synchronously and the formal
experiment checks every returned output against its oracle. Detailed operation
receipts are deferred, and each formal A worker retains one separate diagnostic
receipt rather than a complete physical receipt for every timed call. The
original per-execution receipt requirement was therefore not fulfilled.

The implementation-entry endpoint was revised after an adverse observation.
Both first-result endpoints are lifecycle and import confounded. Post-import is
adverse on all four rows, with a maximum diagnostic block of 2.377129x. The
successor also regressed first-result medians relative to its predecessor while
improving prepared steady execution. Instrumentation qualification covers only
Arm A. No external human authoring or prevalence evidence is included.

Offline recount is not a new GPU execution, a product installation test, a
full historical-authority relocation, external review, or claim authorization.
""",
        "REPLAY_MATRIX.md": """# Replay matrix

| Layer | Included | Offline verifier action |
| --- | --- | --- |
| Formal performance | 160 cells, 20,480 steady samples | Recompute every worker median and all block ratios |
| Lifecycle | A/C/E worker import, gap, post-import, entry, and partitions | Reconcile each worker and compute descriptive medians |
| Instrumentation | 1,024 Arm-A endpoints | Recompute paired block estimator and overhead |
| AOT | 20 fresh-process cache-hit durations plus four cold denominators | Recompute medians and hit/cold ratios |
| Competence | 8 nonformal B/C workers, 1,024 steady samples | Recompute worker medians and C/B ratios |
| GPU execution | Not included | No GPU access |
| Historical full authority | Not portable in this package | Not claimed |
""",
        "DEPENDENCIES.md": """# Components, dependencies, and distribution basis

This peer-review artifact contains only project-authored material intentionally
included for artifact evaluation:

| Component | Distribution basis |
| --- | --- |
| `verify.py` | Project-authored standard-library verifier included as source |
| `data/*.json` | Project-authored anonymous projections derived from retained measurements |
| `*.md` and `manifest.json` | Project-authored documentation and integrity metadata |

No third-party source code, binary, dataset, or proprietary header is bundled.
Offline verification requires Python 3.10 or newer and only its standard
library, which is an external prerequisite rather than a redistributed package
component. Verification performs no network access, GPU execution, package
installation, or project import.

NVIDIA OptiX, CUDA, GPU drivers, measured binaries, proprietary headers, and
signing keys are not distributed. Their original licensing and acquisition
terms therefore remain outside this package. This evidence-only package does
not claim to reconstruct or rerun the historical GPU environment offline.
""",
    }
    return {name: text.encode("utf-8") for name, text in values.items()}


def _build_manifest(public_root: Path) -> dict[str, object]:
    files = []
    for path in sorted(public_root.rglob("*"), key=lambda item: item.relative_to(public_root).as_posix().encode()):
        if path.is_file():
            relative = path.relative_to(public_root).as_posix()
            require(relative != "manifest.json", "manifest existed before construction")
            files.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    body = {
        "schema": "rtdl.cgo2027.submission_evidence.artifact_manifest.v1",
        "file_count": len(files),
        "payload_bytes": sum(row["bytes"] for row in files),
        "files": files,
    }
    return {**body, "manifest_sha256": digest(body)}


def build_archive(public_root: Path) -> bytes:
    names = ["manifest.json"] + [row["path"] for row in strict_json(public_root / "manifest.json")["files"]]
    members = [(name, (public_root / name).read_bytes()) for name in sorted(names, key=lambda item: item.encode())]
    compressed = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=compressed, compresslevel=9, mtime=0
    ) as gz, tarfile.open(
        fileobj=gz, mode="w", format=tarfile.USTAR_FORMAT
    ) as archive:
        for name, payload in members:
            info = tarfile.TarInfo(f"{ARCHIVE_PREFIX}/{name}")
            info.size = len(payload)
            info.mode = 0o444
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.type = tarfile.REGTYPE
            archive.addfile(info, io.BytesIO(payload))
    return compressed.getvalue()


def verify_archive(payload: bytes, public_root: Path) -> None:
    expected = {
        f"{ARCHIVE_PREFIX}/{path.relative_to(public_root).as_posix()}": path.read_bytes()
        for path in public_root.rglob("*")
        if path.is_file()
    }
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        members = archive.getmembers()
        require(len(members) == len(expected), "archive member count differs")
        require({member.name for member in members} == set(expected), "archive member names differ")
        for member in members:
            require(member.isfile() and member.mode == 0o444, "archive member type or mode differs")
            require(member.mtime == 0 and member.uid == 0 and member.gid == 0, "archive metadata differs")
            require(member.uname == "" and member.gname == "", "archive owner metadata differs")
            stream = archive.extractfile(member)
            require(stream is not None and stream.read() == expected[member.name], "archive payload differs")


def require_new_external_output_root(output_root: Path) -> Path:
    require(output_root.is_absolute(), "output root must be an explicit absolute path")
    resolved = output_root.resolve(strict=False)
    require(resolved != ROOT and ROOT not in resolved.parents, "output root must be outside the repository")
    require(not output_root.exists(), "output root already exists; overwrite refused")
    return resolved


def export_package(
    *,
    projection: Mapping[str, object],
    provenance: Mapping[str, object],
    verifier,
    template_root: Path,
    output_root: Path,
) -> dict[str, object]:
    output_root = require_new_external_output_root(output_root)
    frozen_projection = verifier.EXPECTED_PROJECTION_SHA256
    require(frozen_projection != "UNSET_BEFORE_R2_REHEARSAL", "verifier projection identity is not frozen")
    require(projection["projection_sha256"] == frozen_projection, "projection differs from frozen verifier")
    summary = verifier.build_summary(projection)
    output_root.mkdir(parents=True)
    public_root = output_root / "public"
    private_root = output_root / "private"
    public_root.mkdir()
    private_root.mkdir()
    (public_root / "data").mkdir()
    shutil.copyfile(template_root / "verify.py", public_root / "verify.py")
    write_json(public_root / "data" / "performance_projection.json", projection)
    write_json(public_root / "data" / "recount_summary.json", summary)
    for name, payload in _public_documents(summary).items():
        (public_root / name).write_bytes(payload)
    manifest = _build_manifest(public_root)
    write_json(public_root / "manifest.json", manifest)
    public_verification = verifier.verify_artifact(public_root)
    public_files = {
        path.relative_to(public_root).as_posix(): sha256_file(path)
        for path in public_root.rglob("*")
        if path.is_file()
    }
    provenance_body = dict(provenance)
    provenance_seal = provenance_body.pop("provenance_sha256")
    provenance_body["public_files"] = public_files
    provenance_body["template_verifier_sha256"] = sha256_file(template_root / "verify.py")
    provenance_body["public_projection_file_sha256"] = sha256_file(public_root / "data" / "performance_projection.json")
    provenance_body["public_summary_file_sha256"] = sha256_file(public_root / "data" / "recount_summary.json")
    provenance_body["pre_public_file_provenance_sha256"] = provenance_seal
    final_provenance = {**provenance_body, "provenance_sha256": digest(provenance_body)}
    write_json(private_root / "provenance.json", final_provenance)
    first = build_archive(public_root)
    second = build_archive(public_root)
    require(first == second, "two in-process archive builds differ")
    verify_archive(first, public_root)
    archive_path = output_root / "rtdl-cgo2027-artifact.tar.gz"
    archive_path.write_bytes(first)
    receipt_body = {
        "schema": "rtdl.cgo2027.submission_evidence.export_receipt.v1",
        "status": "PASS__RAW_TO_ANONYMOUS_PROJECTION_AND_PACKAGE",
        "projection_sha256": projection["projection_sha256"],
        "summary_sha256": summary["summary_sha256"],
        "manifest_sha256": manifest["manifest_sha256"],
        "archive_sha256": hashlib.sha256(first).hexdigest(),
        "archive_bytes": len(first),
        "archive_member_count": len(public_files),
        "formal_worker_count": 160,
        "formal_steady_sample_count": 20480,
        "instrumentation_worker_count": 1024,
        "aot_qualification_count": 20,
        "nonformal_competence_worker_count": 8,
        "byte_identical_in_process_second_build": True,
        "gpu_execution_performed": False,
        "raw_evidence_mutated": False,
        "private_provenance_in_public_package": False,
        "public_or_manuscript_claim_authorized": False,
        "offline_verification": public_verification,
    }
    receipt = {**receipt_body, "receipt_sha256": digest(receipt_body)}
    write_json(output_root / "EXPORT_RECEIPT.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ada-root", type=Path, required=True)
    parser.add_argument("--ampere-root", type=Path, required=True)
    parser.add_argument("--cross-root", type=Path, required=True)
    parser.add_argument("--template-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        projection, provenance, verifier = collect_projection(
            ada_root=args.ada_root,
            ampere_root=args.ampere_root,
            cross_root=args.cross_root,
            template_root=args.template_root.resolve(),
        )
        receipt = export_package(
            projection=projection,
            provenance=provenance,
            verifier=verifier,
            template_root=args.template_root.resolve(),
            output_root=args.output_root,
        )
    except (OSError, ExportError, TypeError, ValueError) as error:
        print(json.dumps({"status": "REJECT", "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
