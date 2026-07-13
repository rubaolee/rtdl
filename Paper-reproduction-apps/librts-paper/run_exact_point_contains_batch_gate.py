from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from run_exact_point_contains_count_only_gate import run_gate


CASE_MEMBERS = {
    "USACensusBlockGroupBoundaries": (
        "PPoPPAE/datasets/polygons/USACensusBlockGroupBoundaries.wkt",
        "PPoPPAE/datasets/queries/point-contains_queries_100000/USACensusBlockGroupBoundaries.wkt",
    ),
    "USADetailedWaterBodies": (
        "PPoPPAE/datasets/polygons/USADetailedWaterBodies.wkt",
        "PPoPPAE/datasets/queries/point-contains_queries_100000/USADetailedWaterBodies.wkt",
    ),
    "parks_Europe": (
        "PPoPPAE/datasets/polygons/parks_Europe.wkt",
        "PPoPPAE/datasets/queries/point-contains_queries_100000/parks_Europe.wkt",
    ),
    "lakes.bz2": (
        "PPoPPAE/datasets/polygons/lakes.bz2.wkt",
        "PPoPPAE/datasets/queries/point-contains_queries_100000/lakes.bz2.wkt",
    ),
    "parks.bz2": (
        "PPoPPAE/datasets/polygons/parks.bz2.wkt",
        "PPoPPAE/datasets/queries/point-contains_queries_100000/parks.bz2.wkt",
    ),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _member_map(extraction: dict[str, object]) -> dict[str, dict[str, object]]:
    if not extraction.get("claim_boundary", {}).get("archive_subset_extracted", False):
        raise RuntimeError("exact subset extraction is not verified")
    members = extraction.get("extraction", {}).get("selected_members", ())
    result = {}
    for member in members:
        if not isinstance(member, dict) or "relative_path" not in member:
            raise RuntimeError("malformed selected member evidence")
        result[str(member["relative_path"])] = member
    return result


def _resolve_member(
    *,
    extraction: dict[str, object],
    member: str,
) -> Path:
    root = Path(str(extraction["extraction"]["final_path"])).resolve()
    relative = Path(member)
    path = (root / relative).resolve()
    if root not in path.parents:
        raise RuntimeError(f"member escaped extraction root: {member}")
    evidence = _member_map(extraction).get(member)
    if evidence is None:
        raise RuntimeError(f"member missing from extraction evidence: {member}")
    if not path.is_file():
        raise FileNotFoundError(path)
    expected_size = int(evidence["size_bytes"])
    expected_sha = str(evidence["sha256"])
    if path.stat().st_size != expected_size or _sha256(path) != expected_sha:
        raise RuntimeError(f"member hash/size mismatch: {member}")
    return path


def run_batch(
    *,
    author_binary: Path,
    ae_root: Path,
    extraction: dict[str, object],
    archive: dict[str, object],
    output_dir: Path,
    serialize_root: Path,
) -> dict[str, object]:
    cases = {}
    for case_id, (geometry_member, query_member) in CASE_MEMBERS.items():
        geometry = _resolve_member(extraction=extraction, member=geometry_member)
        query = _resolve_member(extraction=extraction, member=query_member)
        result = run_gate(
            author_binary=author_binary,
            ae_root=ae_root,
            geometry_path=geometry,
            query_path=query,
            serialize_dir=serialize_root / case_id,
            archive_result=archive,
            extraction_result=extraction,
        )
        result["case_id"] = case_id
        result_path = output_dir / f"{case_id}.json"
        result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        cases[case_id] = result
    matched = all(bool(item["matched"]) for item in cases.values())
    return {
        "schema": "rtdl.paper_reproduction.librts.exact_point_contains_batch.v2",
        "status": (
            "exact_input_point_contains_batch_matched"
            if matched
            else "exact_input_point_contains_batch_mismatch"
        ),
        "matched": matched,
        "case_count": len(cases),
        "matched_case_count": sum(bool(item["matched"]) for item in cases.values()),
        "same_files_passed_to_author_and_rtdl": True,
        "claim_boundary": {
            "exact_archive_and_extracted_input_identity_used": True,
            "same_input_result_count_agreement": matched,
            "figure6_reproduced": False,
            "performance_ratio_authorized": False,
            "complete_paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-binary", type=Path, required=True)
    parser.add_argument("--ae-root", type=Path, required=True)
    parser.add_argument("--archive-result", type=Path, required=True)
    parser.add_argument("--extraction-result", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--serialize-root", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.serialize_root.mkdir(parents=True, exist_ok=True)
    payload = run_batch(
        author_binary=args.author_binary.resolve(),
        ae_root=args.ae_root.resolve(),
        archive=json.loads(args.archive_result.read_text(encoding="utf-8")),
        extraction=json.loads(args.extraction_result.read_text(encoding="utf-8")),
        output_dir=args.output_dir.resolve(),
        serialize_root=args.serialize_root.resolve(),
    )
    output = args.output_dir / "batch_summary.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
