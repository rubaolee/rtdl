#!/usr/bin/env python3
"""Create or verify the recovered nine-application source manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from experiments.v4_paper_apps_pyoptix.contracts import APP_SPECS

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "Paper-reproduction-apps"
SCHEMA = "rtdl.v4_paper_apps_pyoptix.source_recovery.v1"
REMOTE_ORIGIN = (
    "/home/lestat/work/goal5782_clean_validation_v5/source/Paper-reproduction-apps"
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> dict[str, object]:
    expected_directories = {row.source_directory for row in APP_SPECS}
    actual_directories = {
        path.name
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }
    if actual_directories != expected_directories:
        raise RuntimeError(
            "recovered application directory inventory differs: "
            f"expected={sorted(expected_directories)!r} "
            f"actual={sorted(actual_directories)!r}"
        )
    files = []
    for path in sorted(SOURCE_ROOT.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(ROOT).as_posix()
        files.append(
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": _sha(path),
            }
        )
    apps = []
    for spec in APP_SPECS:
        source = SOURCE_ROOT / spec.source_directory / "v4_whole_app.py"
        observed = _sha(source)
        if observed != spec.v4_source_sha256:
            raise RuntimeError(f"recovered V4 source drift: {spec.app_id}")
        apps.append(
            {
                "app_id": spec.app_id,
                "source_path": source.relative_to(ROOT).as_posix(),
                "v4_source_sha256": observed,
                "historical_identity": spec.historical_identity,
                "bytes_present": True,
                "runnable_claimed_by_manifest": False,
                "executed_claimed_by_manifest": False,
            }
        )
    directory_digest = hashlib.sha256(
        json.dumps(
            files,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    return {
        "schema": SCHEMA,
        "source_origin": REMOTE_ORIGIN,
        "source_origin_copy_count_claimed": 1,
        "matching_historical_directory_count_observed": 42,
        "matching_directories_are_independent_sources_claimed": False,
        "goal5785_final_archive_recovered": False,
        "goal5785_expected_archive_sha256": (
            "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41"
        ),
        "application_count": len(apps),
        "file_count": len(files),
        "directory_manifest_sha256": directory_digest,
        "applications": apps,
        "files": files,
        "claim_boundary": {
            "three_exact_historical_v4_source_hashes_present": True,
            "six_old_historical_authorities_recovered": False,
            "six_sources_available_as_new_candidate_inputs": True,
            "historical_goal5785_execution_replayed": False,
            "performance_result_exists": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if (args.output is None) == (args.verify is None):
        parser.error("choose exactly one of --output or --verify")
    payload = build_manifest()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        if args.verify.read_text(encoding="utf-8") != rendered:
            raise RuntimeError("stored recovered-source manifest differs")
    else:
        assert args.output is not None
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(
        json.dumps(
            {
                "application_count": payload["application_count"],
                "file_count": payload["file_count"],
                "directory_manifest_sha256": payload["directory_manifest_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
