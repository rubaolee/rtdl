"""Independent archive and raw-reducer recount for Goal5758/M1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile

from scripts.goal5758_m1_independent_oracles import (
    checked_u64_product_sum,
    checked_u64_sum,
    keyed_i64_identical_dedup,
)


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize(value):
    if isinstance(value, list):
        return tuple(normalize(item) for item in value)
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items()}
    return value


def recount(archive_path: Path) -> dict[str, object]:
    with tarfile.open(archive_path, "r:gz") as archive:
        members = {
            item.name: archive.extractfile(item).read()
            for item in archive.getmembers() if item.isfile()
        }
    manifest_name = "goal5758_m1_local_evidence/MANIFEST.json"
    manifest = json.loads(members[manifest_name])
    mismatches = []
    for row in manifest["payloads"]:
        data = members.get(row["path"])
        if data is None or len(data) != row["size"] or sha(data) != row["sha256"]:
            mismatches.append(row["path"])
    lanes = []
    for name, data in sorted(members.items()):
        if "/LANES/" not in name:
            continue
        lane = json.loads(data)
        rows = lane["raw_reducer_rows"]
        if lane["reducer_algebra"] == "checked_keyed_i64_sum":
            observed = keyed_i64_identical_dedup(rows, capacity=4096)
        elif lane["reducer_algebra"] == "checked_u64_sum":
            observed = checked_u64_sum(row["count"] for row in rows)
        elif lane["reducer_algebra"] == "checked_u64_product_sum":
            observed = checked_u64_product_sum(
                (row["count"], row["query.weight"]) for row in rows)
        else:
            raise ValueError(lane["reducer_algebra"])
        matched = normalize(lane["observed"]) == normalize(observed)
        lanes.append({
            "app_id": lane["app_id"], "lane_id": lane["lane_id"],
            "reducer_algebra": lane["reducer_algebra"],
            "independently_recomputed": normalize(observed), "matched": matched,
        })
    result = json.loads(members["goal5758_m1_local_evidence/RESULT.json"])
    return {
        "schema": "rtdl.goal5758.m1_independent_recount.v1",
        "archive_sha256": sha(archive_path.read_bytes()),
        "manifest_payload_count": manifest["payload_count"],
        "manifest_payload_bytes": manifest["payload_bytes"],
        "manifest_mismatch_count": len(mismatches),
        "manifest_mismatches": mismatches,
        "lane_count": len(lanes),
        "lane_match_count": sum(item["matched"] for item in lanes),
        "lanes": lanes,
        "submitted_local_pass_count": result["local_pipeline_pass_count"],
        "behavioral_gpu_lane_count": result["behavioral_gpu_lane_count"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = recount(args.archive)
    if result["manifest_mismatch_count"] or result["lane_match_count"] != result["lane_count"]:
        raise RuntimeError(json.dumps(result, sort_keys=True))
    data = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    if args.output:
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.write_text(data, encoding="utf-8")
    print(data, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
