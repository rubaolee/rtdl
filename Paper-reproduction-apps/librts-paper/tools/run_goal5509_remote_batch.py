from __future__ import annotations

import json
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

from run_exact_range_intersects_batch import run_batch


ROOT = Path("/workspace/goal5509")
ARCHIVE = Path("/workspace/librts-data/PPoPPAE-v2.tar.gz")
ARCHIVE_RESULT = ROOT / "librts_goal5479_archive_inventory.json"
OPERATION_INVENTORY = ROOT / "librts_goal5492_exact_archive_operation_inventory.json"
PAIRS = ROOT / "goal5509_range_intersects_next_exact_batch.json"
TARGET = Path("/workspace/librts-targets/goal5509-range-intersects")
BASE_TARGET = Path("/workspace/librts-targets/goal5500-range-intersects")
BASE_EXTRACTION_RESULT = ROOT / "librts_goal5500_range_intersects_batch_extraction.json"
EXTRACTION_RESULT = ROOT / "librts_goal5509_range_intersects_batch_extraction.json"
BATCH_RESULT = ROOT / "librts_goal5509_range_intersects_batch_gate.json"
AUTHOR_BINARY = Path("/workspace/librts-ae/SpatialQueryBenchmark/build/query")
AE_ROOT = Path("/workspace/librts-ae")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    archive_result = json.loads(ARCHIVE_RESULT.read_text(encoding="utf-8"))
    operation_inventory = json.loads(OPERATION_INVENTORY.read_text(encoding="utf-8"))
    pair_rows = json.loads(PAIRS.read_text(encoding="utf-8"))
    # Reuse the six verified geometry members already extracted for Goal5500.
    # Only the new query members are staged, which keeps this batch within the
    # POD quota while preserving the archive and per-file SHA-256 evidence.
    base_extraction = json.loads(BASE_EXTRACTION_RESULT.read_text(encoding="utf-8"))
    selected_queries = [row["query_member"] for row in pair_rows]
    existing = [BASE_TARGET / relative_path for relative_path in selected_queries]
    if all(path.is_file() for path in existing):
        extracted = [
            {
                "relative_path": relative_path,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "reused_after_verified_archive_extraction": True,
            }
            for relative_path, path in zip(selected_queries, existing)
        ]
    else:
        with tempfile.TemporaryDirectory(dir=ROOT, prefix="goal5509-query-stage-") as temp:
            stage = Path(temp) / "selected"
            # GNU tar performs the exact-member extraction in native code and
            # avoids the very slow Python tarfile decompression loop on the POD.
            subprocess.run(
                [
                    "tar",
                    "--extract",
                    "--use-compress-program",
                    "pigz -p 16",
                    "--file",
                    str(ARCHIVE),
                    "--directory",
                    str(stage),
                    "--no-same-owner",
                    "--no-same-permissions",
                    *selected_queries,
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            extracted = []
            for relative_path in selected_queries:
                target = stage / relative_path
                if not target.is_file():
                    raise RuntimeError(f"selected member was not extracted: {relative_path}")
                extracted.append(
                    {
                        "relative_path": relative_path,
                        "size_bytes": target.stat().st_size,
                        "sha256": _sha256(target),
                    }
                )
            if {item["relative_path"] for item in extracted} != set(selected_queries):
                raise RuntimeError("new query batch extraction was incomplete")
            for item in extracted:
                source = stage / item["relative_path"]
                destination = BASE_TARGET / item["relative_path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    raise FileExistsError(f"query member already exists: {destination}")
                source.replace(destination)
    extraction = {
        "schema": "rtdl.paper_reproduction.librts.verified_operation_batch.v1",
        "status": "exact_archive_operation_batch_safely_extended",
        "operation": "range_intersects",
        "archive": base_extraction["archive"],
        "extraction": {
            "final_path": str(BASE_TARGET),
            "selected_pairs": [
                {"geometry": row["geometry_member"], "query": row["query_member"]}
                for row in pair_rows
            ],
            "selected_members": base_extraction["extraction"]["selected_members"] + extracted,
            "selected_pair_count": len(pair_rows),
            "selected_member_count": len(base_extraction["extraction"]["selected_members"]) + len(extracted),
            "reused_verified_geometry_batch": "librts_goal5500_range_intersects_batch_extraction.json",
            "atomic_query_member_stage": True,
        },
        "claim_boundary": {
            "archive_verified": True,
            "archive_subset_extracted": True,
            "exact_input_files_identified": True,
            "paper_figure_reproduced": False,
            "performance_ratio_authorized": False,
            "complete_paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }
    EXTRACTION_RESULT.write_text(json.dumps(extraction, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    cases = []
    for row in pair_rows:
        cases.append(
            {
                "case_id": row["case_id"],
                "geometry": str(BASE_TARGET / row["geometry_member"]),
                "query": str(BASE_TARGET / row["query_member"]),
                "serialize_dir": str(Path("/workspace/librts-serialize/goal5509") / row["case_id"]),
            }
        )
    batch = run_batch(
        author_binary=AUTHOR_BINARY,
        ae_root=AE_ROOT,
        cases=cases,
        archive_result=archive_result,
        extraction_result=extraction,
        author_load_factor="1",
    )
    BATCH_RESULT.write_text(json.dumps(batch, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"extraction": extraction, "batch": batch}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
