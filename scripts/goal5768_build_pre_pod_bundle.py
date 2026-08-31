#!/usr/bin/env python3
"""Build the deterministic Goal5768 three-way pre-POD bundle and twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz"
OUTPUT = ROOT / "history/internal_docs/goal5768_three_way_pre_pod_bundle_v9_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5768_three_way_pre_pod_bundle_v9_twin_20260812.tar.gz"

APP_DIRS = tuple(ROOT / "Paper-reproduction-apps" / name for name in (
    "goal5753-held-out-particle-tracking", "librts-paper", "raydb-paper",
    "rayjoin-paper", "rt-barneshut-paper", "rt-dbscan-paper", "rtnn-paper",
    "triangle-counting-paper", "x-hd-paper",
))
APP_SUPPORT = tuple(
    path.relative_to(ROOT).as_posix()
    for directory in APP_DIRS
    for path in sorted(directory.glob("*.py"))
) + tuple(
    path.relative_to(ROOT).as_posix()
    for path in sorted((
        ROOT / "examples/current/research_benchmarks/triangle_counting"
    ).glob("*")) if path.is_file()
) + tuple(
    path.relative_to(ROOT).as_posix()
    for path in sorted((ROOT / "examples/current/features/graph").glob("*.py"))
) + (
    "Paper-reproduction-apps/librts-paper/data/fixtures/tiny_boxes.wkt",
    "Paper-reproduction-apps/librts-paper/data/fixtures/tiny_range_queries.wkt",
    "Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/border_noise3d_component_signature.csv",
    "Paper-reproduction-apps/rtnn-paper/data/fixtures/goal5531_exact_knn/search.xyz",
    "Paper-reproduction-apps/rtnn-paper/data/fixtures/goal5531_exact_knn/queries.xyz",
    "Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_a.wkt",
    "Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_b.wkt",
    "Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json",
)

OVERLAYS = (
    *(path.relative_to(ROOT).as_posix()
      for path in sorted((ROOT / "src/rtdsl").glob("v4*.py"))),
    *APP_SUPPORT,
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
    "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
    "Paper-reproduction-apps/raydb-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rayjoin-paper/v4_fixtures.py",
    "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rt-barneshut-paper/v4_fixture.py",
    "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py",
    "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
    "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py",
    "scripts/goal5768_audit_v2_v3_v4_performance_eligibility.py",
    "scripts/goal5768_three_way_frontdoors.py",
    "scripts/goal5768_three_way_functional_smoke.py",
    "scripts/goal5768_three_way_worker.py",
    "scripts/goal5768_formal_controller.py",
    "scripts/goal5768_evaluate_three_way_formal.py",
    "scripts/goal5768_recount_three_way_raw.py",
    "scripts/goal5768_target_prepare.py",
    "scripts/goal5768_build_pre_pod_bundle.py",
    "tests/goal5768_performance_eligibility_test.py",
    "tests/goal5768_three_way_frontdoors_test.py",
    "tests/goal5768_formal_harness_test.py",
    "tests/goal5768_pre_pod_bundle_test.py",
    "history/internal_docs/goal5768_application_frontdoor_completion_audit_v5_20260812.json",
    "history/internal_docs/goal5765_integrated_nine_app_recount_20260812.json",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", mtime=0, filename="") as gz:
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
    if not BASE.is_file():
        raise FileNotFoundError(BASE)
    with tarfile.open(BASE, "r:gz") as outer:
        handle = outer.extractfile("SOURCE.tar.gz")
        if handle is None:
            raise RuntimeError("Goal5767 usable RC lacks SOURCE.tar.gz")
        source_bytes = handle.read()
    payloads: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(source_bytes), mode="r:gz") as source:
        for member in source.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            if not parts or path.is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe base member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported base member: {member.name}")
            name = "/".join(parts)
            if name in payloads:
                raise RuntimeError(f"duplicate base member: {name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts):
                raise RuntimeError(f"private/cache base member: {name}")
            if name.endswith((".pyc", "librtdl_optix.so")) \
                    or "/build/" in f"/{name}/":
                raise RuntimeError(f"prebuilt/cache base member: {name}")
            source_handle = source.extractfile(member)
            if source_handle is None:
                raise RuntimeError(f"unreadable base member: {name}")
            payloads[name] = source_handle.read()
    return payloads


def main() -> None:
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
    source_payloads = _base_source()
    for name in OVERLAYS:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        source_payloads[name] = path.read_bytes()
    source = _archive(source_payloads)
    prepare = (ROOT / "scripts/goal5768_target_prepare.py").read_bytes()
    readme = (
        "# Goal5768 V2/V3/V4 exact pre-POD candidate\n\n"
        "This candidate performs only a create-only target prepare: fresh native "
        "build, focused tests and 39 fresh-process functional admissions. It emits "
        "zero formal workers. The 312-worker matrix is impossible without a second "
        "exact owner authority.\n\n"
        "The formal scope is nine applications, thirteen application-owned lanes, "
        "and three methods. It reports 26 independent row-local V2/V4 and V3/V4 "
        "comparisons without compensation. The particle V2/V3 lanes are new frozen "
        "comparison backports, never stock or historical claims.\n"
    ).encode()
    rows = [
        {"path": "SOURCE.tar.gz", "sha256": _sha(source), "size_bytes": len(source)},
        {"path": "HARNESS/goal5768_target_prepare.py", "sha256": _sha(prepare),
         "size_bytes": len(prepare)},
        {"path": "README.md", "sha256": _sha(readme), "size_bytes": len(readme)},
    ]
    manifest = {
        "schema": "rtdl.goal5768.three_way_pre_pod_manifest.v1",
        "goal": 5768,
        "bundle_version": 9,
        "base_goal5767_bundle_sha256": _sha(BASE.read_bytes()),
        "source_archive_sha256": _sha(source),
        "source_file_count": len(source_payloads),
        "source_payload_is_free_of_private_codex_state": True,
        "source_payload_is_free_of_prebuilt_target_native": True,
        "paper_app_count": 9,
        "application_lane_count": 13,
        "method_count": 3,
        "functional_smoke_worker_count": 39,
        "formal_worker_count": 312,
        "independent_comparison_row_count": 26,
        "prepare_is_create_only": True,
        "formal_requires_second_exact_owner_authority": True,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    bundle = _archive({
        "SOURCE.tar.gz": source,
        "HARNESS/goal5768_target_prepare.py": prepare,
        "README.md": readme,
        "PORTABLE_MANIFEST.json": manifest_bytes,
    })
    OUTPUT.write_bytes(bundle)
    TWIN.write_bytes(bundle)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("Goal5768 pre-POD twin differs")
    print(json.dumps({
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": _sha(source),
        "source_file_count": len(source_payloads),
        "outer_payload_count": len(rows),
        "outer_payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
