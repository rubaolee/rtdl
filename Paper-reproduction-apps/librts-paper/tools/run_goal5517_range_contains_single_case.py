from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_exact_range_contains_count_gate import run_gate


BASE_TARGET = Path("/tmp/goal5517-target")
AUTHOR_BINARY = Path("/workspace/librts-ae/SpatialQueryBenchmark/build/query")
AE_ROOT = Path("/workspace/librts-ae")
ARCHIVE_RESULT = Path("/tmp/goal5517/librts_goal5479_pod_download_verified.json")
EXTRACTION_RESULT = Path("/tmp/goal5517/extraction.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--geometry-member", required=True)
    parser.add_argument("--query-member", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-target", type=Path, default=BASE_TARGET)
    parser.add_argument("--archive-result", type=Path, default=ARCHIVE_RESULT)
    parser.add_argument("--extraction-result", type=Path, default=EXTRACTION_RESULT)
    parser.add_argument("--serialize-root", type=Path, default=Path("/tmp/librts-serialize/goal5517"))
    args = parser.parse_args()
    serialize_dir = args.serialize_root / args.case
    serialize_dir.mkdir(parents=True, exist_ok=True)
    result = run_gate(
        author_binary=AUTHOR_BINARY,
        ae_root=AE_ROOT,
        geometry_path=args.base_target / args.geometry_member,
        query_path=args.base_target / args.query_member,
        serialize_dir=serialize_dir,
        archive_result=json.loads(args.archive_result.read_text(encoding="utf-8")),
        extraction_result=json.loads(args.extraction_result.read_text(encoding="utf-8")),
    )
    result["case_id"] = args.case
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
