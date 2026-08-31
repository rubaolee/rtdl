#!/usr/bin/env python3
"""Build the deterministic, V2/V4-only Goal5774 pre-POD bundle."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz"
OUTPUT = ROOT / "history/internal_docs/goal5774_v2_v4_pre_pod_bundle_v13_20260813.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5774_v2_v4_pre_pod_bundle_v13_twin_20260813.tar.gz"

APP_NAMES = (
    "goal5753-held-out-particle-tracking", "librts-paper", "raydb-paper",
    "rayjoin-paper", "rt-barneshut-paper", "rt-dbscan-paper", "rtnn-paper",
    "triangle-counting-paper", "x-hd-paper",
)

# Goal5774 is deliberately V2-direct versus V4.  These files are later V3-only
# prepared-wrapper work and must not drift the reviewed Goal5767 V4 base source.
# The three tracked core files therefore retain their exact base bytes; the two
# app wrappers are absent from the base and remain absent from this bundle.
V3_ONLY_OVERLAY_EXCLUSIONS = frozenset({
    "src/rtdsl/action_ray_triangle_scalar_summary.py",
    "src/rtdsl/generic_primitives.py",
    "src/rtdsl/__init__.py",
    "Paper-reproduction-apps/triangle-counting-paper/rtdl3_action_migration.py",
    "Paper-reproduction-apps/triangle-counting-paper/rtdl3_whole_app.py",
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/rtdl3_whole_app.py",
})


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
            raise RuntimeError("Goal5767 base lacks SOURCE.tar.gz")
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
            handle = source.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable base member: {name}")
            payloads[name] = handle.read()
    return payloads


def _overlay_paths() -> tuple[str, ...]:
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
    selected.update((
        "Paper-reproduction-apps/librts-paper/data/fixtures/tiny_boxes.wkt",
        "Paper-reproduction-apps/librts-paper/data/fixtures/tiny_range_queries.wkt",
        "Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/border_noise3d_component_signature.csv",
        "Paper-reproduction-apps/rtnn-paper/data/fixtures/goal5531_exact_knn/search.xyz",
        "Paper-reproduction-apps/rtnn-paper/data/fixtures/goal5531_exact_knn/queries.xyz",
        "Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_a.wkt",
        "Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_b.wkt",
        "Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json",
        "Paper-reproduction-apps/rtdl3_whole_app_contract.py",
        "scripts/goal5769_rematerialize_fixed_radius_evidence.py",
        "scripts/goal5757_verify_core_freeze.py",
        "scripts/goal5768_three_way_frontdoors.py",
        "scripts/goal5768_target_prepare.py",
        "scripts/goal5774_prepared_three_way_frontdoors.py",
        "scripts/goal5774_home_v2_v4_prepared_validation.py",
        "scripts/goal5774_prepared_v2_v4_worker.py",
        "scripts/goal5774_prepared_v2_v4_controller.py",
        "scripts/goal5774_evaluate_prepared_v2_v4.py",
        "scripts/goal5774_recount_prepared_v2_v4_raw.py",
        "scripts/goal5774_recount_home_v2_v4_prepared.py",
        "scripts/goal5774_build_v2_v4_pre_pod_bundle.py",
        "scripts/goal5774_target_prepare.py",
        "tests/goal5774_v2_v4_prepared_frontdoors_test.py",
        "tests/goal5774_v2_v4_formal_harness_test.py",
        "history/internal_docs/goal5774_v4_prepared_three_way_performance_plan_20260813.md",
        "history/internal_docs/self_review_goal5774_prepared_three_way_performance_plan_20260813.md",
        "history/internal_docs/goal5773_v4_core_successor_manifest_20260813.json",
        "history/internal_docs/goal5769_v4_core_successor_manifest_20260812.json",
    ))
    selected.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tests").glob("goal57*_v4_*test.py")
        if path.is_file())
    selected.difference_update(V3_ONLY_OVERLAY_EXCLUSIONS)
    missing = [name for name in selected if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Goal5774 overlay missing: {missing!r}")
    return tuple(sorted(selected))


def main() -> None:
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
    source_payloads = _base_source()
    overlays = _overlay_paths()
    for name in overlays:
        source_payloads[name] = (ROOT / name).read_bytes()
    source = _archive(source_payloads)
    prepare = (ROOT / "scripts/goal5774_target_prepare.py").read_bytes()
    readme = (
        "# Goal5774 exact V2-direct versus V4 prepared candidate\n\n"
        "This bundle contains nine Paper Apps / thirteen application-owned lanes. "
        "Each method prepares one owner, executes one distinct exact/true-OptiX "
        "activation whose seconds are reported but unregistered, then two distinct "
        "registered calls. The create-only target prepare emits zero formal workers. "
        "The 208-worker matrix requires a second exact owner authority. V3 is not "
        "executed or required. Cold Goal5769 evidence is not replaced.\n"
    ).encode("utf-8")
    rows = [
        {"path": "SOURCE.tar.gz", "sha256": _sha(source), "size_bytes": len(source)},
        {"path": "HARNESS/goal5774_target_prepare.py", "sha256": _sha(prepare),
         "size_bytes": len(prepare)},
        {"path": "README.md", "sha256": _sha(readme), "size_bytes": len(readme)},
    ]
    manifest = {
        "schema": "rtdl.goal5774.v2_v4_pre_pod_manifest.v1",
        "goal": 5774,
        "bundle_version": 13,
        "base_bundle_sha256": _sha(BASE.read_bytes()),
        "source_archive_sha256": _sha(source),
        "source_file_count": len(source_payloads),
        "overlay_file_count": len(overlays),
        "paper_app_count": 9,
        "application_lane_count": 13,
        "method_count": 2,
        "activation_call_count_per_functional_gate": 26,
        "measured_shape_call_count_per_functional_gate": 52,
        "formal_worker_count": 208,
        "independent_comparison_row_count": 26,
        "v3_required_or_executed": False,
        "v3_only_overlay_exclusions": sorted(V3_ONLY_OVERLAY_EXCLUSIONS),
        "source_payload_is_free_of_private_codex_state": True,
        "source_payload_is_free_of_prebuilt_target_native": True,
        "prepare_is_create_only": True,
        "formal_requires_second_exact_owner_authority": True,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    bundle = _archive({
        "SOURCE.tar.gz": source,
        "HARNESS/goal5774_target_prepare.py": prepare,
        "README.md": readme,
        "PORTABLE_MANIFEST.json": manifest_bytes,
    })
    OUTPUT.write_bytes(bundle)
    TWIN.write_bytes(bundle)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("Goal5774 deterministic twin differs")
    print(json.dumps({
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": _sha(source),
        "source_file_count": len(source_payloads),
        "overlay_file_count": len(overlays),
        "outer_payload_count": len(rows),
        "outer_payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
