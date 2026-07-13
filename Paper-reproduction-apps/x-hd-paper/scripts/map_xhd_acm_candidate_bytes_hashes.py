#!/usr/bin/env python3
"""Map ACM supplement candidate bytes to hash-manifest entries for X-HD.

This app-owned helper is the conservative follow-up to
``ingest_xhd_acm_artifact_instructions.py``. It inspects a local ACM supplement
zip, parses simple SHA256 manifest lines, and reports whether candidate input
or archive entries are covered by matching hashes. It does not extract private
material into the repository, run POD, run author binaries, run RTDL, or claim
exact paper reproduction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
import zipfile
from typing import Any, Dict, Iterable, List, Tuple

from ingest_xhd_acm_artifact_instructions import ingest_zip


SHA256_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _parse_hash_manifest_text(path: str, text: str) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        matches = list(SHA256_RE.finditer(line))
        if not matches:
            continue
        digest = matches[0].group(0).lower()
        before = line[: matches[0].start()].strip()
        after = line[matches[0].end() :].strip()
        target = after or before
        target = target.lstrip("*").strip()
        if not target:
            continue
        entries.append(
            {
                "manifest_path": path,
                "line_no": line_no,
                "sha256": digest,
                "target": target.replace("\\", "/"),
                "raw_line": raw_line,
            }
        )
    return entries


def _load_hash_entries(zf: zipfile.ZipFile, hash_records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    seen = set()
    for record in hash_records:
        path = str(record["path"])
        if path in seen:
            continue
        seen.add(path)
        data = zf.read(path)
        entries.extend(_parse_hash_manifest_text(path, _safe_decode(data)))
    return entries


def _candidate_match(candidate_path: str, candidate_sha: str, hash_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    normalized = candidate_path.replace("\\", "/")
    basename = pathlib.PurePosixPath(normalized).name
    same_name = [
        entry
        for entry in hash_entries
        if entry["target"] == normalized or pathlib.PurePosixPath(entry["target"]).name == basename
    ]
    same_digest = [entry for entry in hash_entries if entry["sha256"] == candidate_sha]
    exact = [entry for entry in same_name if entry["sha256"] == candidate_sha]

    if exact:
        status = "matched_by_path_and_sha256"
    elif same_name:
        status = "hash_mismatch_for_named_candidate"
    elif same_digest:
        status = "matched_by_sha256_only"
    else:
        status = "no_hash_manifest_match"

    return {
        "path": normalized,
        "sha256": candidate_sha,
        "status": status,
        "matching_entries": exact or same_digest or same_name,
    }


def _dedupe_candidate_records(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    candidates: List[Dict[str, Any]] = []
    for record in records:
        if record.get("category") != "candidate_input_or_archive":
            continue
        key = (record["path"], record["sha256"])
        if key in seen:
            continue
        seen.add(key)
        candidates.append(record)
    return sorted(candidates, key=lambda r: str(r["path"]))


def _decide(mapping_records: List[Dict[str, Any]], hash_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    statuses = {record["status"] for record in mapping_records}
    if not mapping_records:
        status = "no_candidate_bytes_to_map"
        follow_up = "record_no_candidate_bytes"
    elif "hash_mismatch_for_named_candidate" in statuses:
        status = "candidate_hash_mismatch_detected"
        follow_up = "candidate_hash_mismatch_review"
    elif statuses and statuses <= {"matched_by_path_and_sha256", "matched_by_sha256_only"}:
        status = "all_candidate_hashes_matched__workload_mapping_required"
        follow_up = "candidate_workload_mapping_review"
    elif hash_entries:
        status = "partial_or_missing_candidate_hash_mapping"
        follow_up = "candidate_hash_mapping_gap_review"
    else:
        status = "candidate_bytes_without_parseable_hash_manifest"
        follow_up = "candidate_identity_review"
    return {
        "status": status,
        "recommended_goal_type": follow_up,
        "pod_allowed_next": False,
        "requires_workload_mapping_before_pod": True,
    }


def build_mapping(zip_path: pathlib.Path) -> Dict[str, Any]:
    zip_path = zip_path.resolve()
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"not a zip file: {zip_path}")

    ingestion = ingest_zip(zip_path)
    records = ingestion["records"]
    candidates = _dedupe_candidate_records(records)
    hash_records = [record for record in records if record.get("category") == "hash_or_manifest"]

    with zipfile.ZipFile(zip_path) as zf:
        hash_entries = _load_hash_entries(zf, hash_records)

    mappings = [
        _candidate_match(str(candidate["path"]), str(candidate["sha256"]), hash_entries)
        for candidate in candidates
    ]
    decision = _decide(mappings, hash_entries)

    return {
        "schema": "rtdl.paper_reproduction.xhd.acm_candidate_bytes_hash_mapping.v1",
        "zip_filename": zip_path.name,
        "zip_sha256": _sha256_bytes(zip_path.read_bytes()),
        "ingestion_schema": ingestion["schema"],
        "candidate_count": len(candidates),
        "hash_manifest_entry_count": len(hash_entries),
        "candidate_mappings": mappings,
        "classification": decision["status"],
        "recommended_goal_type": decision["recommended_goal_type"],
        "pod_allowed_next": decision["pod_allowed_next"],
        "requires_workload_mapping_before_pod": decision["requires_workload_mapping_before_pod"],
        "sufficient_to_claim_exact_input": False,
        "claim_boundary": {
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "not_allowed": [
            "running POD directly from this mapping",
            "claiming candidate bytes are exact paper inputs from hashes alone",
            "claiming Figure 5 reproduction from this mapping alone",
            "claiming full X-HD paper reproduction from this mapping alone",
            "claiming author-vs-RTDL performance ratio from this mapping alone",
        ],
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        mapping = build_mapping(args.zip_path)
    except Exception as exc:
        print(f"candidate bytes/hash mapping failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(mapping, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
