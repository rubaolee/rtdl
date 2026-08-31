#!/usr/bin/env python3
"""Build the deterministic, no-private-cache Goal5782 local candidate.

The candidate starts from the exact Goal5776 v9 portable source and overlays
only the reviewed Goal5778/Goal5782 product, functional and verification
surface.  It deliberately carries no native binary and no target result.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "history/internal_docs/goal5776_v2_v4_real_scale_pre_pod_source_v9_20260814.tar.gz"
APP_NAMES = (
    "goal5753-held-out-particle-tracking", "librts-paper", "raydb-paper",
    "rayjoin-paper", "rt-barneshut-paper", "rt-dbscan-paper", "rtnn-paper",
    "triangle-counting-paper", "x-hd-paper",
)
FIXTURES = (
    "Paper-reproduction-apps/librts-paper/data/fixtures/tiny_boxes.wkt",
    "Paper-reproduction-apps/librts-paper/data/fixtures/tiny_range_queries.wkt",
    "Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/border_noise3d_component_signature.csv",
    "Paper-reproduction-apps/rtnn-paper/data/fixtures/goal5531_exact_knn/search.xyz",
    "Paper-reproduction-apps/rtnn-paper/data/fixtures/goal5531_exact_knn/queries.xyz",
    "Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_a.wkt",
    "Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_b.wkt",
    "Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json",
)
SCRIPTS = (
    "scripts/goal5764_home_hierarchy_frontier_validation.py",
    "scripts/goal5764_m6_hierarchy_fixtures.py",
    "scripts/goal5768_three_way_frontdoors.py",
    "scripts/goal5768_three_way_functional_smoke.py",
    "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
    "scripts/goal5773_home_multiround_lifecycle_validation.py",
    "scripts/goal5778_home_checked_u64_reduction_validation.py",
    "scripts/goal5778_home_triangle_checked_reduction_validation.py",
    "scripts/goal5782_recount_home_functional.py",
    # The frozen X-HD V2-direct front door loads its historical true-OptiX
    # implementation from this app-local module.  Include that implementation
    # and only its two actual helper imports; omitting it made a host-worktree
    # smoke pass while the clean portable source failed.
    "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py",
    "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py",
    "Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py",
)
TESTS = (
    "tests/goal5764_v4_hierarchy_frontier_test.py",
    "tests/goal5773_v4_prepared_hierarchy_lifecycle_test.py",
    "tests/goal5776_v4_hierarchy_single_materialization_test.py",
    "tests/goal5776_v4_triangle_device_columns_test.py",
    "tests/goal5778_v4_checked_u64_device_reduction_test.py",
    "tests/goal5782_canonical_packed_hierarchy_binding_test.py",
)
V3_ONLY_EXCLUSIONS = frozenset({
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/rtdl3_whole_app.py",
    "Paper-reproduction-apps/triangle-counting-paper/rtdl3_action_migration.py",
    "Paper-reproduction-apps/triangle-counting-paper/rtdl3_whole_app.py",
})


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def read_base() -> dict[str, bytes]:
    if not BASE.is_file():
        raise FileNotFoundError(BASE)
    payloads: dict[str, bytes] = {}
    with tarfile.open(BASE, "r:gz") as source:
        for member in source.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or path.is_absolute() or ".." in parts or name in payloads:
                raise RuntimeError(f"unsafe/duplicate base member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported base member: {member.name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts) \
                    or name.endswith((".pyc", "librtdl_optix.so")) \
                    or "/build/" in f"/{name}/":
                raise RuntimeError(f"private/prebuilt base member: {name}")
            handle = source.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable base member: {name}")
            payloads[name] = handle.read()
    # The old source manifest describes the old tree and must never be retained.
    payloads.pop("history/internal_docs/goal5776_source_file_manifest.json", None)
    return payloads


def overlay_names() -> tuple[str, ...]:
    names: set[str] = set(SCRIPTS) | set(TESTS) | set(FIXTURES)
    for directory in (ROOT / "src/rtdsl", ROOT / "src/native/optix"):
        names.update(
            path.relative_to(ROOT).as_posix()
            for path in directory.glob("*") if path.is_file())
    for app in APP_NAMES:
        names.update(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "Paper-reproduction-apps" / app).glob("*.py")
            if path.is_file())
    for directory in (
        ROOT / "examples/current/research_benchmarks/triangle_counting",
        ROOT / "examples/current/features/graph",
    ):
        names.update(
            path.relative_to(ROOT).as_posix()
            for path in directory.glob("*") if path.is_file())
    names.add("Paper-reproduction-apps/rtdl3_whole_app_contract.py")
    # Goal5782 is the V2/V4 candidate.  Preserve the exact Goal5776 rule that
    # these post-baseline V3 application files are not silently added to it.
    names.difference_update(V3_ONLY_EXCLUSIONS)
    missing = [name for name in names if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Goal5782 overlay missing: {missing!r}")
    return tuple(sorted(names))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--source-output", type=Path, required=True)
    parser.add_argument("--source-twin", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output, args.twin, args.source_output, args.source_twin):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)

    source_payloads = read_base()
    overlays = overlay_names()
    for name in overlays:
        source_payloads[name] = (ROOT / name).read_bytes()
    rows = [{"path": name, "size_bytes": len(data), "sha256": sha(data)}
            for name, data in sorted(source_payloads.items())]
    source_manifest = (json.dumps({
        "schema": "rtdl.goal5782.portable_source_manifest.v1",
        "base_source_sha256": sha(BASE.read_bytes()),
        "file_count": len(rows), "files": rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    source_payloads[
        "history/internal_docs/goal5782_portable_source_manifest.json"
    ] = source_manifest
    source_bytes = archive(source_payloads)
    validator = (ROOT / "scripts/goal5782_home_clean_validate.py").read_bytes()
    recount = (ROOT / "scripts/goal5782_recount_home_functional.py").read_bytes()
    readme = (
        "# Goal5782 local functional release candidate\n\n"
        "This deterministic candidate contains source only. It builds a fresh "
        "native, rematerializes proof evidence, runs focused changed-mechanism "
        "tests and 26 V2/V4 functional workers for all nine Paper Apps. It "
        "cannot create formal performance workers or authorize a POD.\n"
    ).encode()
    outer_rows = [
        {"path": "SOURCE.tar.gz", "sha256": sha(source_bytes),
         "size_bytes": len(source_bytes)},
        {"path": "HARNESS/goal5782_home_clean_validate.py", "sha256": sha(validator),
         "size_bytes": len(validator)},
        {"path": "HARNESS/goal5782_recount_home_functional.py", "sha256": sha(recount),
         "size_bytes": len(recount)},
        {"path": "README.md", "sha256": sha(readme), "size_bytes": len(readme)},
    ]
    manifest = (json.dumps({
        "schema": "rtdl.goal5782.local_functional_candidate_manifest.v1",
        "goal": 5782, "bundle_version": 5,
        "source_archive_sha256": sha(source_bytes),
        "source_file_count": len(source_payloads),
        "overlay_file_count": len(overlays),
        "paper_app_count": 9, "application_lane_count": 13,
        "functional_worker_count": 26,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "source_free_of_private_codex_state": True,
        "source_free_of_prebuilt_native": True,
        "pod_authorized": False,
        "payload_count": len(outer_rows),
        "payload_bytes": sum(row["size_bytes"] for row in outer_rows),
        "payloads": outer_rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    bundle = archive({
        "SOURCE.tar.gz": source_bytes,
        "HARNESS/goal5782_home_clean_validate.py": validator,
        "HARNESS/goal5782_recount_home_functional.py": recount,
        "README.md": readme,
        "PORTABLE_MANIFEST.json": manifest,
    })
    for path, data in (
        (args.output, bundle), (args.twin, bundle),
        (args.source_output, source_bytes), (args.source_twin, source_bytes),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if args.output.read_bytes() != args.twin.read_bytes() \
            or args.source_output.read_bytes() != args.source_twin.read_bytes():
        raise RuntimeError("Goal5782 deterministic twin differs")
    print(json.dumps({
        "bundle_sha256": sha(bundle),
        "source_archive_sha256": sha(source_bytes),
        "source_file_count": len(source_payloads),
        "overlay_file_count": len(overlays),
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
