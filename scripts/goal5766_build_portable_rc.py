#!/usr/bin/env python3
"""Build deterministic, self-contained Goal5766 portable V4 RC archives."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE_SOURCE = ROOT / "history/internal_docs/goal5765_home_execution_source_20260812.tar.gz"
OUTPUT = ROOT / "history/internal_docs/goal5766_v4_portable_rc_v3_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5766_v4_portable_rc_v3_twin_20260812.tar.gz"

TESTS = tuple(
    f"tests/{path.name}" for path in sorted((ROOT / "tests").glob("goal57*_v4_*test.py"))
)
OVERLAYS = TESTS + (
    "scripts/goal5749_v4_callback_poc_driver.py",
    "scripts/goal5749_modern_rtx_executor.sh",
    "scripts/goal5754_validate_typed_physical_schema_design.py",
    "scripts/goal5757_verify_core_freeze.py",
    "scripts/goal5759_recount_home_triangle_reduction.py",
    "scripts/goal5760_recount_home_bounded_relation.py",
    "scripts/goal5761_recount_home_multiround_spatial.py",
    "scripts/goal5762_recount_home_exact_predicate_witness.py",
    "scripts/goal5763_recount_home_grouped_event_reduction.py",
    "scripts/goal5764_recount_home_hierarchy_frontier.py",
    "scripts/goal5765_integrated_nine_app_recount.py",
    "history/internal_docs/goal5749_amendment_a1_composed_numba_leaf_policy_20260811.json",
    "history/internal_docs/goal5753_held_out_particle_tracking_exam_result_20260811.json",
    "history/internal_docs/goal5753_held_out_particle_tracking_exam_evidence_20260811.tar.gz",
    "history/internal_docs/goal5754_typed_physical_schema_design_20260811.json",
    "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json",
    "history/internal_docs/goal5757_v4_core_freeze_manifest_20260811.json",
    "history/internal_docs/goal5757_v4_nine_app_migration_batches_20260811.json",
    "history/internal_docs/goal5761_preimplementation_rtnn_contract_reconciliation_20260812.json",
    "history/internal_docs/goal5759_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5760_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5761_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5762_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5763_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5764_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5765_nine_app_single_identity_result_20260812.json",
    "history/internal_docs/goal5765_nine_app_single_identity_technical_report_20260812.md",
    "examples/current/research_benchmarks/hierarchy_coverage/v4_hierarchy_coverage_app.py",
    "examples/current/research_benchmarks/hierarchy_coverage/README.md",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _gzip_tar(payloads: dict[str, bytes]) -> bytes:
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith(".py") else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return compressed.getvalue()


def _complete_source() -> bytes:
    payloads: dict[str, bytes] = {}
    with tarfile.open(BASE_SOURCE, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            if not parts or member.isdir():
                continue
            if path.is_absolute() or ".." in parts or not member.isfile():
                raise RuntimeError(f"unsafe base source member: {member.name}")
            name = "/".join(parts)
            if name in payloads:
                raise RuntimeError(f"duplicate base source member: {name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts):
                raise RuntimeError(f"private/cache base member: {name}")
            if name.endswith(".pyc") or name.endswith("librtdl_optix.so"):
                raise RuntimeError(f"prebuilt/cache base member: {name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable base source member: {name}")
            payloads[name] = handle.read()
    for name in OVERLAYS:
        data = (ROOT / name).read_bytes()
        payloads[name] = data
    return _gzip_tar(payloads)


def main() -> None:
    if len(TESTS) != 19:
        raise RuntimeError(f"expected 19 V4 test modules, found {len(TESTS)}")
    source = _complete_source()
    driver_name = "HARNESS/goal5766_portable_validate.py"
    driver = (ROOT / "scripts/goal5766_portable_validate.py").read_bytes()
    readme = (
        "# RTDL V4 portable functional release candidate\n\n"
        "This archive contains source, never a prebuilt target native. On a clean Linux "
        "NVIDIA/OptiX machine, extract this archive and run:\n\n"
        "```bash\npython3 HARNESS/goal5766_portable_validate.py \\\n"
        "  --bundle-root . --work-root /tmp/rtdl_v4_rc \\\n"
        "  --optix-prefix $HOME/vendor/optix-dev --cuda-prefix /usr/lib/cuda --cc 61\n```\n\n"
        "The command builds a fresh native, runs 180 unit tests, executes the nine-app "
        "13-paper-lane functional matrix, and independently recounts it. It registers "
        "no performance timing.\n"
    ).encode()
    rows = [
        {"path": "SOURCE.tar.gz", "sha256": _sha(source), "size_bytes": len(source)},
        {"path": driver_name, "sha256": _sha(driver), "size_bytes": len(driver)},
        {"path": "README.md", "sha256": _sha(readme), "size_bytes": len(readme)},
    ]
    manifest = {
        "schema": "rtdl.goal5766.portable_manifest.v1",
        "goal": 5766,
        "source_archive_sha256": _sha(source),
        "source_payload_is_free_of_prebuilt_target_native": True,
        "source_payload_is_free_of_private_codex_state": True,
        "v4_test_module_count": len(TESTS),
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    outer = _gzip_tar({
        "SOURCE.tar.gz": source,
        driver_name: driver,
        "README.md": readme,
        "PORTABLE_MANIFEST.json": manifest_bytes,
    })
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(outer)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("portable twin mismatch")
    print(json.dumps({
        "bundle_sha256": _sha(outer),
        "source_archive_sha256": _sha(source),
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "test_module_count": len(TESTS),
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
