#!/usr/bin/env python3
"""Build the deterministic Goal5776 V2-direct versus V4 pre-POD bundle."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz"
SOURCE_MANIFEST_MEMBER = "history/internal_docs/goal5776_source_file_manifest.json"
APP_NAMES = (
    "goal5753-held-out-particle-tracking", "librts-paper", "raydb-paper",
    "rayjoin-paper", "rt-barneshut-paper", "rt-dbscan-paper", "rtnn-paper",
    "triangle-counting-paper", "x-hd-paper",
)
V3_ONLY_OVERLAY_EXCLUSIONS = frozenset({
    "src/rtdsl/action_ray_triangle_scalar_summary.py",
    "src/rtdsl/generic_primitives.py",
    "src/rtdsl/__init__.py",
    "Paper-reproduction-apps/triangle-counting-paper/rtdl3_action_migration.py",
    "Paper-reproduction-apps/triangle-counting-paper/rtdl3_whole_app.py",
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/rtdl3_whole_app.py",
})
REQUIRED_LEGACY_SCRIPT_DEPENDENCIES = frozenset({
    "scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py",
    "scripts/goal5773_home_multiround_lifecycle_validation.py",
})


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
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


def _base_source() -> dict[str, bytes]:
    with tarfile.open(BASE, "r:gz") as outer:
        handle = outer.extractfile("SOURCE.tar.gz")
        if handle is None:
            raise RuntimeError("Goal5767 base lacks SOURCE.tar.gz")
        source_bytes = handle.read()
    result: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(source_bytes), mode="r:gz") as archive:
        for member in archive.getmembers():
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in result:
                raise RuntimeError(f"unsafe/duplicate base member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported base member: {member.name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts) \
                    or name.endswith((".pyc", "librtdl_optix.so")) \
                    or "/build/" in f"/{name}/":
                raise RuntimeError(f"private/prebuilt base member: {name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable base member: {name}")
            result[name] = handle.read()
    return result


def _overlays() -> tuple[str, ...]:
    selected: set[str] = set()
    for root in (ROOT / "src/rtdsl", ROOT / "src/native/optix"):
        selected.update(
            path.relative_to(ROOT).as_posix()
            for path in root.glob("*") if path.is_file())
    for name in APP_NAMES:
        directory = ROOT / "Paper-reproduction-apps" / name
        selected.update(
            path.relative_to(ROOT).as_posix()
            for path in directory.glob("*.py") if path.is_file())
    for directory in (
        ROOT / "examples/current/research_benchmarks/triangle_counting",
        ROOT / "examples/current/features/graph",
    ):
        selected.update(
            path.relative_to(ROOT).as_posix()
            for path in directory.glob("*") if path.is_file())
    selected.update({
        "Paper-reproduction-apps/rtdl3_whole_app_contract.py",
        "scripts/goal5757_verify_core_freeze.py",
        "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
        "scripts/goal5776_build_real_scale_data_bundle.py",
        "scripts/goal5776_build_pre_pod_bundle.py",
        "scripts/goal5776_verify_source_file_manifest.py",
        "scripts/goal5776_target_prepare.py",
        "scripts/goal5776_target_real_scale_functional_prepare.py",
        "scripts/goal5776_real_scale_formal_contract.py",
        "scripts/goal5776_real_scale_runtime_inputs.py",
        "scripts/goal5776_real_scale_frontdoors.py",
        "scripts/goal5776_real_scale_formal_worker.py",
        "scripts/goal5776_real_scale_formal_controller.py",
        "scripts/goal5776_evaluate_real_scale_v2_v4.py",
        "scripts/goal5776_recount_real_scale_v2_v4_raw.py",
        "scripts/goal5776_close_formal_result.py",
        "scripts/goal5776_build_formal_result_evidence.py",
        "scripts/goal5776_estimate_formal_runtime.py",
        "scripts/goal5776_symmetric_endpoint.py",
    })
    # The target runs the complete Goal5776 focused suite from the clean
    # archive.  Package every Goal5776 helper consumed by that suite, not only
    # the formal controller surface, plus the two frozen legacy readers the
    # real application fixtures import.  Omitting these files would make a
    # host-worktree test pass while the exact portable source fails.
    selected.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts").glob("goal5776*") if path.is_file())
    selected.update(REQUIRED_LEGACY_SCRIPT_DEPENDENCIES)
    selected.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tests").glob("goal5776*test.py") if path.is_file())
    selected.difference_update(V3_ONLY_OVERLAY_EXCLUSIONS)
    missing = [name for name in selected if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Goal5776 overlay missing: {missing!r}")
    return tuple(sorted(selected))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-bundle", type=Path, required=True)
    parser.add_argument("--runtime-budget", type=Path, required=True)
    parser.add_argument("--expected-value-statement", type=Path, required=True)
    parser.add_argument("--focused-test-count", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--source-output", type=Path)
    parser.add_argument("--source-twin", type=Path)
    args = parser.parse_args()
    requested_outputs = [args.output, args.twin]
    requested_outputs.extend(
        path for path in (args.source_output, args.source_twin)
        if path is not None)
    for path in requested_outputs:
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    if args.focused_test_count <= 0:
        raise ValueError("focused test count must be positive")
    data = args.data_bundle.resolve()
    if not data.is_file():
        raise FileNotFoundError(data)
    budget_path = args.runtime_budget.resolve()
    if not budget_path.is_file():
        raise FileNotFoundError(budget_path)
    budget = json.loads(budget_path.read_text(encoding="utf-8"))
    budget_seconds = float(budget.get("conservative_budget_seconds", 0.0))
    if (
        budget.get("schema")
        != "rtdl.goal5776.home_derived_formal_runtime_budget.v1"
        or budget.get("not_a_performance_result") is not True
        or budget.get("worker_count") != 464
        or budget.get("formal_method_lifecycle_units") != 58
        or budget.get("owner_must_confirm_budget_before_worker_zero") is not True
        or not math.isfinite(budget_seconds) or budget_seconds <= 0.0
    ):
        raise RuntimeError("Goal5776 runtime budget is ineligible")
    budget_bytes = budget_path.read_bytes()
    expectation_path = args.expected_value_statement.resolve()
    if not expectation_path.is_file():
        raise FileNotFoundError(expectation_path)
    expectation_bytes = expectation_path.read_bytes()
    expectation_text = expectation_bytes.decode("utf-8")
    for required in (
        "1 pass / 25 fail", "0 pass / 26 fail",
        "many, possibly all", "No repair, retry, resume, replacement",
    ):
        if required not in expectation_text:
            raise RuntimeError(
                f"Goal5776 expected-value statement omitted: {required}")
    source_payloads = _base_source()
    overlays = _overlays()
    for name in overlays:
        source_payloads[name] = (ROOT / name).read_bytes()
    source_rows = [{
        "path": name, "size_bytes": len(data), "sha256": _sha(data),
    } for name, data in sorted(source_payloads.items())]
    source_manifest = (json.dumps({
        "schema": "rtdl.goal5776.source_file_manifest.v1",
        "file_count": len(source_rows), "files": source_rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    source_payloads[SOURCE_MANIFEST_MEMBER] = source_manifest
    source = _archive(source_payloads)
    prepare = (ROOT / "scripts/goal5776_target_prepare.py").read_bytes()
    readme = (
        "# Goal5776 exact real-scale V2-direct versus V4 candidate\n\n"
        "Nine Paper Apps and 15 real-scale execution units. The worker "
        "arithmetic is (15 cold + 14 prepared) unit-lifecycles * 8 pairs * "
        "2 methods = 464 fresh processes. The statistical output contains "
        "34 independent rows: 15 cold rows, 13 ordinary prepared rows, and "
        "6 RayJoin prepared batch rows. RayJoin's six prepared rows come from "
        "the same 16 workers, so row count must not be multiplied by workers "
        "per row. Seventeen additional RT-DBSCAN proof cases remain mandatory "
        "functional-only attacks. The exact "
        "data bundle is separately pinned. Target preparation builds a fresh "
        "native, rematerializes fixed-radius proof evidence, executes 126 untimed "
        "real-scale functional paths while populating the target leaf cache, "
        "then seals that cache. It emits zero formal workers. Formal execution "
        "requires a second exact owner authority. V3 is not required or run.\n"
    ).encode()
    payloads = [
        {"path": "SOURCE.tar.gz", "sha256": _sha(source), "size_bytes": len(source)},
        {"path": "HARNESS/goal5776_target_prepare.py", "sha256": _sha(prepare),
         "size_bytes": len(prepare)},
        {"path": "README.md", "sha256": _sha(readme), "size_bytes": len(readme)},
        {"path": "RUNTIME_BUDGET.json", "sha256": _sha(budget_bytes),
         "size_bytes": len(budget_bytes)},
        {"path": "EXPECTED_VALUE_STATEMENT.md",
         "sha256": _sha(expectation_bytes),
         "size_bytes": len(expectation_bytes)},
    ]
    manifest = {
        "schema": "rtdl.goal5776.real_scale_pre_pod_manifest.v1",
        "goal": 5776, "bundle_version": 9,
        "base_bundle_sha256": _sha_file(BASE),
        "source_archive_sha256": _sha(source),
        "source_file_count": len(source_payloads),
        "overlay_file_count": len(overlays),
        "data_archive_sha256": _sha_file(data),
        "runtime_budget_sha256": _sha(budget_bytes),
        "expected_value_statement_sha256": _sha(expectation_bytes),
        "conservative_budget_seconds": budget_seconds,
        "paper_app_count": 9, "functional_execution_unit_count": 32,
        "formal_execution_unit_count": 15,
        "cold_execution_unit_count": 15,
        "prepared_execution_unit_count": 14,
        "functional_trial_count": 126,
        "formal_worker_count": 464,
        "independent_comparison_row_count": 34,
        "focused_test_count": args.focused_test_count,
        "v3_required_or_executed": False,
        "source_payload_is_free_of_private_codex_state": True,
        "source_payload_is_free_of_prebuilt_target_native": True,
        "prepare_is_create_only": True,
        "formal_requires_second_exact_owner_authority": True,
        "v3_only_overlay_exclusions": sorted(V3_ONLY_OVERLAY_EXCLUSIONS),
        "payload_count": len(payloads),
        "payload_bytes": sum(row["size_bytes"] for row in payloads),
        "payloads": payloads,
    }
    manifest_bytes = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode()
    bundle = _archive({
        "SOURCE.tar.gz": source,
        "HARNESS/goal5776_target_prepare.py": prepare,
        "README.md": readme,
        "RUNTIME_BUDGET.json": budget_bytes,
        "EXPECTED_VALUE_STATEMENT.md": expectation_bytes,
        "PORTABLE_MANIFEST.json": manifest_bytes,
    })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(bundle)
    args.twin.write_bytes(bundle)
    if args.output.read_bytes() != args.twin.read_bytes():
        raise RuntimeError("Goal5776 deterministic twin differs")
    if args.source_output is not None:
        args.source_output.parent.mkdir(parents=True, exist_ok=True)
        args.source_output.write_bytes(source)
    if args.source_twin is not None:
        args.source_twin.parent.mkdir(parents=True, exist_ok=True)
        args.source_twin.write_bytes(source)
    if (args.source_output is not None and args.source_twin is not None
            and args.source_output.read_bytes() != args.source_twin.read_bytes()):
        raise RuntimeError("Goal5776 deterministic source twin differs")
    print(json.dumps({
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": _sha(source),
        "data_archive_sha256": _sha_file(data),
        "runtime_budget_sha256": _sha(budget_bytes),
        "expected_value_statement_sha256": _sha(expectation_bytes),
        "conservative_budget_seconds": budget_seconds,
        "source_file_count": len(source_payloads),
        "overlay_file_count": len(overlays),
        "focused_test_count": args.focused_test_count,
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
