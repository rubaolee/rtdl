#!/usr/bin/env python3
"""Classify artifact-like contents of an X-HD ACM supplement zip.

This app-owned helper is the follow-up to ``inspect_xhd_acm_supplement_zip.py``.
It computes per-entry hashes for artifact-like files and emits an ingestion
manifest. It does not run author binaries, run RTDL, extract private material
into the public repository, or claim exact paper reproduction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import zipfile
from typing import Any, Dict, Iterable, List


DATASET_SUFFIXES = (
    ".ply",
    ".off",
    ".wkt",
    ".nii",
    ".nii.gz",
    ".csv",
    ".tsv",
    ".parquet",
    ".jsonl",
)
ARCHIVE_SUFFIXES = (".zip", ".tar", ".tgz", ".tar.gz", ".tar.zst", ".7z", ".bz2", ".gz")
HASH_TOKENS = ("sha256", "sha-256", "checksum", "checksums", "hash", "manifest", "md5")
DATASET_TOKENS = ("hddatasets", "dataset", "datasets", "input", "inputs", "dragon", "buddha", "brats", "water", "zipcode", "county")
SCRIPT_SUFFIXES = (".sh", ".py", ".ps1", ".bat", ".cu", ".cpp", ".cmake")
SCRIPT_TOKENS = ("readme", "artifact", "reproduce", "regenerate", "download", "prepare", "run_", "script", "instructions")


def _is_hash(path: str) -> bool:
    lower = path.lower()
    return any(token in lower for token in HASH_TOKENS)


def _is_dataset_or_archive(path: str) -> bool:
    lower = path.lower()
    return lower.endswith(DATASET_SUFFIXES) or lower.endswith(ARCHIVE_SUFFIXES) or any(
        token in lower for token in DATASET_TOKENS
    )


def _is_script(path: str) -> bool:
    lower = path.lower()
    return lower.endswith(SCRIPT_SUFFIXES)


def _is_instruction(path: str) -> bool:
    lower = path.lower()
    return any(token in lower for token in SCRIPT_TOKENS)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _entry_record(zf: zipfile.ZipFile, name: str, category: str) -> Dict[str, Any]:
    data = zf.read(name)
    return {
        "path": name,
        "category": category,
        "size": len(data),
        "sha256": _sha256_bytes(data),
    }


def _classify_name(name: str) -> List[str]:
    categories: List[str] = []
    if _is_hash(name):
        categories.append("hash_or_manifest")
    if _is_dataset_or_archive(name):
        categories.append("candidate_input_or_archive")
    if _is_script(name):
        categories.append("script")
    if _is_instruction(name):
        categories.append("instruction")
    return categories


def _decide_next_action(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    categories = {record["category"] for record in records}
    has_candidate = "candidate_input_or_archive" in categories
    has_hash = "hash_or_manifest" in categories
    has_script = "script" in categories
    has_instruction = "instruction" in categories

    if has_candidate and has_hash:
        return {
            "status": "candidate_bytes_and_hash_material_found",
            "recommended_goal_type": "acm_candidate_bytes_hash_mapping_gate",
            "summary": "Candidate input/archive bytes and hash/manifest material exist. Map entries to paper workloads and verify hashes before any author/RTDL POD gate.",
            "pod_allowed_next": False,
        }
    if has_candidate:
        return {
            "status": "candidate_bytes_without_hash_material_found",
            "recommended_goal_type": "acm_candidate_bytes_identity_review",
            "summary": "Candidate input/archive bytes exist but no hash/manifest material was found. Record hashes and request author mapping before POD.",
            "pod_allowed_next": False,
        }
    if has_script or has_instruction:
        return {
            "status": "script_or_instruction_material_found",
            "recommended_goal_type": "acm_regeneration_or_instruction_review",
            "summary": "Scripts or instructions exist without candidate input bytes. Review them for byte-identical regeneration before POD.",
            "pod_allowed_next": False,
        }
    return {
        "status": "no_actionable_artifact_material_found",
        "recommended_goal_type": "record_acm_no_actionable_artifact",
        "summary": "No actionable dataset, hash, script, or instruction material was detected.",
        "pod_allowed_next": False,
    }


def ingest_zip(zip_path: pathlib.Path) -> Dict[str, Any]:
    zip_path = zip_path.resolve()
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"not a zip file: {zip_path}")

    records: List[Dict[str, Any]] = []
    with zipfile.ZipFile(zip_path) as zf:
        names = [info.filename for info in zf.infolist() if not info.is_dir()]
        for name in names:
            categories = _classify_name(name)
            for category in categories:
                records.append(_entry_record(zf, name, category))

    decision = _decide_next_action(records)
    return {
        "schema": "rtdl.paper_reproduction.xhd.acm_artifact_instruction_ingestion_manifest.v1",
        "zip_filename": zip_path.name,
        "zip_sha256": _sha256_bytes(zip_path.read_bytes()),
        "total_artifact_like_records": len(records),
        "records": sorted(records, key=lambda r: (r["category"], r["path"])),
        "classification": decision["status"],
        "recommended_goal_type": decision["recommended_goal_type"],
        "recommendation": decision["summary"],
        "pod_allowed_next": decision["pod_allowed_next"],
        "requires_review_before_pod": True,
        "sufficient_to_claim_exact_input": False,
        "claim_boundary": {
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "not_allowed": [
            "running POD directly from this manifest",
            "claiming exact paper dataset reproduction from this manifest alone",
            "claiming Figure 5 reproduction from this manifest alone",
            "claiming full X-HD paper reproduction from this manifest alone",
            "claiming author-vs-RTDL performance ratio from this manifest alone",
        ],
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        manifest = ingest_zip(args.zip_path)
    except Exception as exc:
        print(f"artifact instruction ingestion failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(manifest, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
