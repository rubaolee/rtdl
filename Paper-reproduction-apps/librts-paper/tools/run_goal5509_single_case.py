from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_exact_range_intersects_count_gate import run_gate


ROOT = Path("/workspace/goal5509")
BASE_TARGET = Path("/workspace/librts-targets/goal5500-range-intersects")
AUTHOR_BINARY = Path("/workspace/librts-ae/SpatialQueryBenchmark/build/query")
AE_ROOT = Path("/workspace/librts-ae")
ARCHIVE_RESULT = ROOT / "librts_goal5479_archive_inventory.json"
EXTRACTION_RESULT = ROOT / "librts_goal5509_range_intersects_batch_extraction.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--geometry-member", required=True)
    parser.add_argument("--query-member", required=True)
    parser.add_argument(
        "--extraction-result",
        type=Path,
        default=EXTRACTION_RESULT,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_gate(
        author_binary=AUTHOR_BINARY,
        ae_root=AE_ROOT,
        geometry_path=BASE_TARGET / args.geometry_member,
        query_path=BASE_TARGET / args.query_member,
        serialize_dir=Path("/workspace/librts-serialize/goal5509") / args.case,
        archive_result=json.loads(ARCHIVE_RESULT.read_text(encoding="utf-8")),
        extraction_result=json.loads(args.extraction_result.read_text(encoding="utf-8")),
        author_load_factor="1",
    )
    result["case_id"] = args.case
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
