#!/usr/bin/env python3
"""Build a provenance bridge for a selected X-HD paper-log input target.

The first supported target is ``graphics_dragon_happy_buddha`` from Goal5177.
It connects the author paper-branch log record to locally acquired public
Stanford files and existing Level B fixtures.

The bridge is provenance only. Matching point counts and source family do not
prove exact paper input identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


STANFORD_URLS = {
    "dragon_archive": "https://graphics.stanford.edu/pub/3Dscanrep/dragon/dragon_recon.tar.gz",
    "happy_archive": "https://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz",
    "asian_dragon_archive": "https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_dragon.ply.gz",
}

TARGETS = {
    "graphics_dragon_happy_buddha": {
        "status": "graphics_dragon_happy_buddha_public_stanford_candidate_bridged__level_b_only",
        "author_basenames": ("dragon.ply", "happy_buddha.ply"),
        "candidate_files": {
            "dragon.ply": "data/external/stanford/dragon_recon/dragon_vrip.ply",
            "happy_buddha.ply": "data/external/stanford/happy_recon/happy_vrip.ply",
        },
        "candidate_archives": {
            "dragon.ply": "data/external/stanford/dragon_recon.tar.gz",
            "happy_buddha.ply": "data/external/stanford/happy_recon.tar.gz",
        },
        "representative_fixtures": {
            "dragon.ply": "data/fixtures/stanford_dragon_res4_full.ply",
            "happy_buddha.ply": "data/fixtures/stanford_happy_res4_full.ply",
        },
        "representative_summaries": {
            "dragon.ply": "results/stanford_dragon_res4_full_summary.json",
            "happy_buddha.ply": "results/stanford_happy_res4_full_summary.json",
        },
    },
    "graphics_dragon_asian_dragon": {
        "status": "graphics_dragon_asian_dragon_public_stanford_candidate_bridged__level_b_only",
        "author_basenames": ("dragon.ply", "asian_dragon.ply"),
        "candidate_files": {
            "dragon.ply": "data/external/stanford/dragon_recon/dragon_vrip.ply",
            "asian_dragon.ply": "data/external/stanford/asian_dragon.ply",
        },
        "candidate_archives": {
            "dragon.ply": "data/external/stanford/dragon_recon.tar.gz",
            "asian_dragon.ply": "data/external/stanford/xyzrgb_dragon.ply.gz",
        },
        "representative_fixtures": {},
        "representative_summaries": {},
    }
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def read_ply_header(path: Path) -> dict[str, Any]:
    vertex_count: int | None = None
    face_count: int | None = None
    fmt: str | None = None
    header_rows: list[str] = []
    with path.open("rb") as fh:
        for line in fh:
            text = line.decode("ascii").strip()
            header_rows.append(text)
            if len(header_rows) == 1 and text != "ply":
                raise ValueError(f"{path} is not a PLY file")
            if text.startswith("format "):
                fmt = text.replace("format ", "", 1)
            elif text.startswith("element vertex "):
                vertex_count = int(text.split()[-1])
            elif text.startswith("element face "):
                face_count = int(text.split()[-1])
            elif text == "end_header":
                break
        else:
            raise ValueError(f"{path} PLY header has no end_header")
    if vertex_count is None:
        raise ValueError(f"{path} PLY header has no vertex count")
    return {
        "format": fmt,
        "vertex_count": vertex_count,
        "face_count": face_count,
        "header_line_count": len(header_rows),
    }


def _find_priority_subset(mapping: dict[str, Any], name: str) -> dict[str, Any]:
    for row in mapping.get("priority_subsets", []):
        if row.get("name") == name:
            return row
    raise ValueError(f"priority subset not found in mapping: {name}")


def _author_records_for_target(log_index: dict[str, Any], basenames: tuple[str, str]) -> list[dict[str, Any]]:
    required = set(basenames)
    rows = []
    for record in log_index.get("run_all_records", []):
        names = {
            item.get("basename")
            for item in record.get("input", {}).get("files", [])
            if isinstance(item, dict)
        }
        if required.issubset(names):
            rows.append(record)
    return rows


def _author_file_facts(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    facts: dict[str, dict[str, Any]] = {}
    for record in records:
        for item in record.get("input", {}).get("files", []):
            if not isinstance(item, dict):
                continue
            basename = item.get("basename")
            if not basename:
                continue
            existing = facts.setdefault(
                str(basename),
                {
                    "basename": basename,
                    "paths": set(),
                    "num_points": set(),
                    "gini_index": set(),
                    "exact_status": set(),
                },
            )
            existing["paths"].add(item.get("path"))
            existing["num_points"].add(item.get("num_points"))
            existing["gini_index"].add(item.get("gini_index"))
            existing["exact_status"].add(item.get("exact_status"))
    normalized: dict[str, dict[str, Any]] = {}
    for key, value in facts.items():
        normalized[key] = {
            "basename": value["basename"],
            "paths": sorted(path for path in value["paths"] if path is not None),
            "num_points": sorted(v for v in value["num_points"] if v is not None),
            "gini_index": sorted(v for v in value["gini_index"] if v is not None),
            "exact_status": sorted(v for v in value["exact_status"] if v is not None),
        }
    return normalized


def _file_artifact(path: Path, *, kind: str) -> dict[str, Any]:
    item = {
        "kind": kind,
        "path": str(path),
        "exists": path.exists(),
    }
    if path.exists():
        item.update({"bytes": path.stat().st_size, "sha256": sha256_file(path)})
        if path.suffix.lower() == ".ply":
            item["ply_header"] = read_ply_header(path)
    return item


def build_bridge(
    *,
    app_root: Path,
    mapping: dict[str, Any],
    log_index: dict[str, Any],
    target: str,
) -> dict[str, Any]:
    if target not in TARGETS:
        raise ValueError(f"unsupported target: {target}")
    spec = TARGETS[target]
    subset = _find_priority_subset(mapping, target)
    author_records = _author_records_for_target(log_index, spec["author_basenames"])
    if not author_records:
        raise ValueError(f"no author run_all records found for target: {target}")
    author_facts = _author_file_facts(author_records)
    candidates: dict[str, dict[str, Any]] = {}
    for basename, rel in spec["candidate_files"].items():
        candidate = _file_artifact(app_root / rel, kind="public_stanford_full_ply_candidate")
        expected_counts = author_facts.get(basename, {}).get("num_points", [])
        vertex_count = candidate.get("ply_header", {}).get("vertex_count")
        candidate["author_log_num_points"] = expected_counts
        candidate["point_count_matches_author_log"] = (
            vertex_count in expected_counts if vertex_count is not None else False
        )
        candidate["exact_paper_identity_proved"] = False
        candidates[basename] = candidate

    archives = {
        basename: _file_artifact(app_root / rel, kind="public_stanford_source_archive")
        for basename, rel in spec["candidate_archives"].items()
    }
    representative_fixtures = {
        basename: _file_artifact(app_root / rel, kind="level_b_res4_fixture")
        for basename, rel in spec["representative_fixtures"].items()
    }
    representative_summaries = {}
    for basename, rel in spec["representative_summaries"].items():
        path = app_root / rel
        representative_summaries[basename] = {
            "path": str(path),
            "exists": path.exists(),
            "summary": json.loads(path.read_text()) if path.exists() else None,
        }

    all_full_candidates_present = all(item["exists"] for item in candidates.values())
    all_point_counts_match = all(
        item.get("point_count_matches_author_log") for item in candidates.values()
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.priority_input_bridge.v1",
        "goal": "Goal5178",
        "status": spec.get("status", f"{target}_public_candidate_bridged__level_b_only"),
        "target": target,
        "author_basename_order": list(spec["author_basenames"]),
        "source_basename": spec["author_basenames"][0],
        "target_basename": spec["author_basenames"][1],
        "source_urls": STANFORD_URLS,
        "goal5177_priority_subset": {
            "name": subset.get("name"),
            "status": subset.get("status"),
            "record_count": subset.get("record_summary", {}).get("record_count"),
            "blocker": subset.get("blocker"),
        },
        "author_log_records": {
            "record_count": len(author_records),
            "sections": sorted({str(row.get("section")) for row in author_records}),
            "hd_results": sorted(
                {
                    row.get("hd_result")
                    for row in author_records
                    if isinstance(row.get("hd_result"), (int, float))
                }
            ),
            "running_avg_times": [
                {
                    "section": row.get("section"),
                    "config": row.get("config"),
                    "avg_time": row.get("running", {}).get("avg_time"),
                    "reported_time_median": row.get("running", {}).get("reported_time_median"),
                }
                for row in author_records
            ],
            "files": author_facts,
        },
        "public_same_source_candidates": candidates,
        "public_source_archives": archives,
        "representative_res4_fixtures": representative_fixtures,
        "representative_res4_summaries": representative_summaries,
        "bridge_assessment": {
            "all_full_public_candidates_present": all_full_candidates_present,
            "full_public_candidate_point_counts_match_author_logs": all_point_counts_match,
            "strong_same_source_candidate": bool(all_full_candidates_present and all_point_counts_match),
            "exact_paper_dataset_identity_proved": False,
            "reason_exact_not_proved": [
                "author logs provide paths and point counts but not input file hashes",
                "local public files use Stanford archive names, not the author's /local/storage/shared/HDDatasets/graphics file bytes",
                "no author conversion script/hash proves byte identity",
            ],
        },
        "claim_boundary": {
            "level_b_same_source_candidate_claimed": bool(
                all_full_candidates_present and all_point_counts_match
            ),
            "exact_paper_dataset_reproduction_claimed": False,
            "figure_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
        "authorized_next_steps": [
            "Use the full public Stanford candidate files for an explicitly Level B large-input feasibility plan.",
            "Do not call this Level C exact paper input unless author file hashes or deterministic conversion provenance appear.",
            "Avoid pairwise exact route attempts at full 437645 x 543652 scale unless a scalable route is selected.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-root", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--log-index", required=True, type=Path)
    parser.add_argument("--target", default="graphics_dragon_happy_buddha")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    bridge = build_bridge(
        app_root=args.app_root,
        mapping=json.loads(args.mapping.read_text()),
        log_index=json.loads(args.log_index.read_text()),
        target=args.target,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bridge, indent=2, sort_keys=True) + "\n")
    print(
        "wrote",
        args.output,
        "target=",
        bridge["target"],
        "same_source=",
        bridge["bridge_assessment"]["strong_same_source_candidate"],
        "exact=",
        bridge["bridge_assessment"]["exact_paper_dataset_identity_proved"],
    )


if __name__ == "__main__":
    main()
