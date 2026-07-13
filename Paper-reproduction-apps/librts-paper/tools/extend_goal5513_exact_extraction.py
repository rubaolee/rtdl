from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path("/tmp/goal5513")
BASE_RESULT = Path("/workspace/goal5509/librts_goal5500_range_intersects_batch_extraction.json")
OUTPUT = ROOT / "librts_goal5513_range_intersects_batch_extraction.json"
FINAL_PATH = Path("/workspace/librts-targets/goal5500-range-intersects")
QUERY_FAMILY = "PPoPPAE/datasets/queries/range-intersects_select_0.01_queries_10000"
MEMBERS = [
    f"{QUERY_FAMILY}/parks_Europe.wkt",
    f"{QUERY_FAMILY}/dtl_cnty.wkt",
    f"{QUERY_FAMILY}/USACensusBlockGroupBoundaries.wkt",
    f"{QUERY_FAMILY}/USADetailedWaterBodies.wkt",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    payload = json.loads(BASE_RESULT.read_text(encoding="utf-8"))
    selected = payload["extraction"]["selected_members"]
    existing = {item["relative_path"] for item in selected}
    for relative_path in MEMBERS:
        if relative_path in existing:
            continue
        path = FINAL_PATH / relative_path
        if not path.is_file():
            raise FileNotFoundError(path)
        selected.append(
            {
                "relative_path": relative_path,
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "reused_verified_archive_extraction": True,
            }
        )
    payload["schema"] = "rtdl.paper_reproduction.librts.verified_operation_batch.v1"
    payload["status"] = "exact_archive_operation_batch_safely_extended"
    payload["extraction"]["selected_members"] = selected
    payload["extraction"]["selected_member_count"] = len(selected)
    payload["extraction"]["additional_query_family"] = "range-intersects_select_0.01_queries_10000"
    payload["extraction"]["additional_query_member_count"] = len(MEMBERS)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
