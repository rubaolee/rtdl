#!/usr/bin/env python3
"""Build deterministic, reviewer-visible evidence for one Goal5776 cohort."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

from goal5776_real_scale_formal_contract import schedule, statistical_rows


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _tree_payloads(root: Path, prefix: str) -> dict[str, bytes]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"evidence tree is not a real directory: {root}")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"evidence tree contains a symlink: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"evidence tree contains a special file: {path}")
        name = f"{prefix}/{path.relative_to(root).as_posix()}"
        result[name] = path.read_bytes()
    return result


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return output.getvalue()


def build(
    *, raw_root: Path, closeout_root: Path, runtime_path: Path,
    plan_path: Path, prepared_path: Path, authority_path: Path,
    output: Path, twin: Path,
) -> dict[str, object]:
    for path in (output, twin):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    if (
        runtime.get("schema") != "rtdl.goal5776.real_scale_runtime.v1"
        or prepared.get("schema")
            != "rtdl.goal5776.create_only_target_prepare_result.v1"
        or plan.get("schema") != "rtdl.goal5776.real_scale_plan.v1"
    ):
        raise RuntimeError("Goal5776 evidence identity schema mismatch")
    if _sha_file(plan_path) != runtime["plan_sha256"]:
        raise RuntimeError("Goal5776 evidence plan/runtime mismatch")
    runtime_sha256 = _sha_file(runtime_path)
    common = (
        "bundle_sha256", "data_archive_sha256",
        "execution_source_sha256", "rtdbscan_evidence_sha256",
        "native_library_sha256", "target_identity_sha256",
        "prepared_identity_sha256", "formal_identity_sha256",
        "plan_sha256", "leaf_cache_manifest_sha256",
        "runtime_budget_sha256", "conservative_budget_seconds",
        "expected_value_statement_sha256",
    )
    if prepared.get("runtime_sha256") != runtime_sha256:
        raise RuntimeError("Goal5776 evidence prepared/runtime byte mismatch")
    for key in common:
        if prepared.get(key) != runtime.get(key):
            raise RuntimeError(
                f"Goal5776 evidence prepared/runtime mismatch: {key}")
    if (
        prepared.get("all_126_functional_trials_correct_and_behavioral_true_optix")
        is not True
        or prepared.get("formal_worker_count") != 0
        or prepared.get("registered_formal_timing_count") != 0
        or prepared.get("formal_requires_second_exact_owner_authority") is not True
    ):
        raise RuntimeError("Goal5776 evidence prepared gate is incomplete")
    functional_root = Path(str(runtime.get("target_functional_root", ""))).resolve()
    functional_summary = functional_root / "SUMMARY.json"
    if (
        not functional_root.is_dir()
        or not functional_summary.is_file()
        or _sha_file(functional_summary)
        != runtime.get("target_functional_summary_sha256")
        or prepared.get("target_functional_summary_sha256")
        != runtime.get("target_functional_summary_sha256")
    ):
        raise RuntimeError("Goal5776 target functional evidence is incomplete")
    functional_files = sorted(
        path for path in functional_root.rglob("*") if path.is_file())
    if len(functional_files) != 127 \
            or any(path.is_symlink() for path in functional_files):
        raise RuntimeError("Goal5776 target functional payload shape is incomplete")
    functional_records = sorted(
        functional_root.glob("[0-9][0-9][0-9].json"))
    functional_digest = hashlib.sha256()
    for path in functional_records:
        functional_digest.update(path.name.encode("utf-8"))
        functional_digest.update(b"\0")
        functional_digest.update(bytes.fromhex(_sha_file(path)))
    functional_summary_payload = json.loads(
        functional_summary.read_text(encoding="utf-8"))
    if (
        len(functional_records) != 126
        or functional_summary_payload.get("functional_trial_count") != 126
        or int(functional_summary_payload.get(
            "cache_population_observation_count", 0)) <= 0
        or functional_summary_payload.get("cache_population_cost_is_free") is not False
        or functional_summary_payload.get(
            "cache_population_observation_is_not_formal_performance") is not True
        or functional_summary_payload.get("functional_records_sha256")
        != functional_digest.hexdigest()
    ):
        raise RuntimeError("Goal5776 target functional records are not bound")
    for key in (
        "bundle_sha256", "data_archive_sha256", "prepared_identity_sha256",
        "target_identity_sha256", "formal_identity_sha256",
        "runtime_budget_sha256", "conservative_budget_seconds",
        "expected_value_statement_sha256",
    ):
        if plan.get(key) != runtime.get(key):
            raise RuntimeError(f"Goal5776 evidence plan/runtime mismatch: {key}")
    authority_body = dict(authority)
    claimed_authority = authority_body.pop("authority_sha256", None)
    if claimed_authority != _digest(authority_body):
        raise RuntimeError("Goal5776 evidence formal authority digest mismatch")
    if (
        authority.get("schema") != "rtdl.goal5776.owner_formal_authority.v2"
        or authority.get("runtime_sha256") != runtime_sha256
        or authority.get("expected_worker_count") != len(schedule())
        or authority.get("expected_independent_row_count") != len(statistical_rows())
        or authority.get("owner_authorized_exactly_once") is not True
        or authority.get("repair_retry_resume_replacement_allowed") is not False
        or float(authority.get("owner_confirmed_conservative_budget_seconds", 0.0))
        != float(runtime.get("conservative_budget_seconds", 0.0))
    ):
        raise RuntimeError("Goal5776 evidence formal authority is ineligible")
    for key in (
        *(item for item in common if item != "conservative_budget_seconds"),
        "formal_contract_sha256",
    ):
        if authority.get(key) != runtime.get(key):
            raise RuntimeError(
                f"Goal5776 evidence authority/runtime mismatch: {key}")
    identity_paths = {
        "IDENTITY/RUNTIME.json": runtime_path,
        "IDENTITY/PLAN.json": plan_path,
        "IDENTITY/PREPARED.json": prepared_path,
        "IDENTITY/FORMAL_AUTHORITY.json": authority_path,
        "EXECUTION/EXECUTION_SOURCE.tar.gz": Path(
            str(runtime["execution_source_path"])),
        "EXECUTION/librtdl_optix.so": Path(str(runtime["native_library_path"])),
        "EXECUTION/FORMAL_NUMBA_LEAF_CACHE_MANIFEST.json": Path(
            str(runtime["leaf_cache_manifest_path"])),
        "EXECUTION/FIXED_RADIUS_REFINEMENT_EVIDENCE.json": Path(
            str(runtime["rtdbscan_evidence_path"])),
        "EXECUTION/DATA_MANIFEST.json": Path(str(runtime["data_manifest_path"])),
        "EXECUTION/RUNTIME_BUDGET.json": Path(str(runtime["runtime_budget_path"])),
        "EXECUTION/EXPECTED_VALUE_STATEMENT.md": Path(
            str(runtime["expected_value_statement_path"])),
    }
    expected_hashes = {
        "EXECUTION/EXECUTION_SOURCE.tar.gz": runtime["execution_source_sha256"],
        "EXECUTION/librtdl_optix.so": runtime["native_library_sha256"],
        "EXECUTION/RUNTIME_BUDGET.json": runtime["runtime_budget_sha256"],
        "EXECUTION/EXPECTED_VALUE_STATEMENT.md": runtime[
            "expected_value_statement_sha256"],
        "EXECUTION/FORMAL_NUMBA_LEAF_CACHE_MANIFEST.json": runtime[
            "leaf_cache_manifest_sha256"],
        "EXECUTION/FIXED_RADIUS_REFINEMENT_EVIDENCE.json": runtime[
            "rtdbscan_evidence_sha256"],
        "EXECUTION/DATA_MANIFEST.json": runtime["data_manifest_sha256"],
    }
    payloads = {
        name: path.resolve().read_bytes() for name, path in identity_paths.items()
        if path.resolve().is_file() and not path.resolve().is_symlink()
    }
    if set(payloads) != set(identity_paths):
        raise FileNotFoundError("Goal5776 evidence identity payload is absent")
    for name, expected in expected_hashes.items():
        if _sha(payloads[name]) != expected:
            raise RuntimeError(f"Goal5776 evidence identity mismatch: {name}")
    payloads.update(_tree_payloads(raw_root.resolve(), "RAW"))
    payloads.update(_tree_payloads(closeout_root.resolve(), "RESULT"))
    payloads.update(_tree_payloads(
        functional_root, "PREPARE/TARGET_FUNCTIONAL"))
    payloads.update(_tree_payloads(
        Path(str(runtime["leaf_cache_root"])).resolve(),
        "EXECUTION/FORMAL_NUMBA_LEAF_CACHE",
    ))
    if len(list((raw_root / "workers").glob("*.json"))) != len(schedule()):
        raise RuntimeError("Goal5776 evidence requires every formal raw worker")
    final = json.loads((closeout_root / "FINAL.json").read_text(encoding="utf-8"))
    if not final.get("measurement_complete") \
            or final.get("worker_count") != len(schedule()):
        raise RuntimeError("Goal5776 evidence closeout is incomplete")
    rows = [{"path": name, "size_bytes": len(data), "sha256": _sha(data)}
            for name, data in sorted(payloads.items())]
    manifest = {
        "schema": "rtdl.goal5776.real_scale_formal_evidence_manifest.v1",
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["size_bytes"]) for row in rows),
        "worker_count": len(schedule()),
        "independent_row_count": len(statistical_rows()),
        "bundle_sha256": runtime["bundle_sha256"],
        "data_archive_sha256": runtime["data_archive_sha256"],
        "execution_source_sha256": runtime["execution_source_sha256"],
        "native_library_sha256": runtime["native_library_sha256"],
        "runtime_budget_sha256": runtime["runtime_budget_sha256"],
        "conservative_budget_seconds": runtime["conservative_budget_seconds"],
        "target_functional_payload_count": len(functional_files),
        "plan_sha256": runtime["plan_sha256"],
        "runtime_sha256": runtime_sha256,
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode()
    archive = _archive({
        **payloads,
        "GOAL5776_EVIDENCE_MANIFEST.json": manifest_bytes,
    })
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive)
    twin.write_bytes(archive)
    if output.read_bytes() != twin.read_bytes():
        raise RuntimeError("Goal5776 evidence twin differs")
    return {
        "archive_sha256": _sha(archive),
        "manifest_sha256": _sha(manifest_bytes),
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "worker_count": len(schedule()),
        "twin_byte_identical": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--closeout-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--formal-authority", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(
        raw_root=args.raw_root, closeout_root=args.closeout_root,
        runtime_path=args.runtime, plan_path=args.plan,
        prepared_path=args.prepared, authority_path=args.formal_authority,
        output=args.output, twin=args.twin,
    ), sort_keys=True))


if __name__ == "__main__":
    main()
