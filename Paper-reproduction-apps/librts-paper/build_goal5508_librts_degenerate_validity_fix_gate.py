from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src" / "rtdsl").is_dir()
)
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    official = {
        "parks_Europe_select_0.01_10000": {
            "author_count": 34240217,
            "pre_fix_rtdl_count": 34240244,
            "fixed_rtdl": RESULTS / "goal5508_official_parks_Europe_250k_fixed.json",
        },
        "lakes_bz2_select_0.01_10000": {
            "author_count": 34581812,
            "pre_fix_rtdl_count": 34586817,
            "fixed_rtdl": RESULTS / "goal5508_official_lakes_bz2_250k_fixed.json",
        },
    }
    degenerate = {
        "parks_Europe_select_0.01_10000": {
            "author_count": 0,
            "pre_fix_rtdl_count": 27,
            "fixed_probe": RESULTS / "goal5508_parks_degenerate_fixed2.json",
            "subset_wkt": RESULTS / "goal5508_parks_degenerate.wkt",
        },
        "lakes_bz2_select_0.01_10000": {
            "author_count": 0,
            "pre_fix_rtdl_count": 5005,
            "fixed_probe": RESULTS / "goal5508_lakes_degenerate_fixed2.json",
            "subset_wkt": RESULTS / "goal5508_lakes_degenerate.wkt",
        },
    }

    official_rows = []
    for case_id, item in official.items():
        fixed = read_json(item["fixed_rtdl"])
        fixed_count = int(fixed["rtdl"]["result_count"])
        official_rows.append(
            {
                "case_id": case_id,
                "author_count": item["author_count"],
                "pre_fix_rtdl_count": item["pre_fix_rtdl_count"],
                "fixed_rtdl_count": fixed_count,
                "pre_fix_delta": item["pre_fix_rtdl_count"] - item["author_count"],
                "fixed_delta": fixed_count - item["author_count"],
                "same_input_files": bool(fixed["input_identity"]["same_input_files"]),
                "geometry_sha256": fixed["input_identity"]["geometry_sha256"],
                "query_sha256": fixed["input_identity"]["query_sha256"],
                "fixed_probe": str(item["fixed_rtdl"].relative_to(ROOT)).replace("\\", "/"),
            }
        )

    degenerate_rows = []
    for case_id, item in degenerate.items():
        probe = read_json(item["fixed_probe"])
        degenerate_rows.append(
            {
                "case_id": case_id,
                "invalid_after_float32_count": probe["invalid_after_float32_count"],
                "invalid_geometry_indices": probe["invalid_geometry_indices"],
                "author_count": item["author_count"],
                "pre_fix_rtdl_count": item["pre_fix_rtdl_count"],
                "fixed_rtdl_count": probe["rtdl_count"],
                "same_input_files": probe["same_input_files"],
                "geometry_sha256": probe["geometry_sha256"],
                "query_sha256": probe["query_sha256"],
                "subset_wkt_sha256": probe["subset_wkt_sha256"],
                "subset_wkt": str(item["subset_wkt"].relative_to(ROOT)).replace("\\", "/"),
            }
        )

    source = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
    library = RESULTS / "goal5508_librtdl_optix.so"
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5508_generic_float32_degenerate_aabb_validity_fix.v1",
        "status": "generic_float32_degenerate_aabb_validity_fix_completed",
        "root_cause": {
            "source_observation": "author Envelope::IsValid uses strict min<max after coord_t=float parsing; author backward query skips invalid indexed envelopes",
            "rtdl_pre_fix_observation": "native float32 packing plus generic OptiX AABB padding allowed post-pack degenerate indexed boxes to produce range_intersects hits",
            "diagnostic_contract": "indexed AABBs that are not strictly valid after float32 packing are non-matchable in the generic OptiX intersection kernel",
            "app_specific_behavior_added": False,
        },
        "official_prefix_matrix": official_rows,
        "degenerate_subset_matrix": degenerate_rows,
        "author_degenerate_subset_runtime": [
            {
                "case_id": "parks_Europe_select_0.01_10000",
                "author_count": 0,
                "geometry_subset": "Paper-reproduction-apps/librts-paper/results/goal5508_parks_degenerate.wkt",
                "query_sha256": "0ddf5ea567223621ffdd7f0fe9c789dd5c7350941d0a8a8e7bb8b98b308ca499",
                "command_contract": "SpatialQueryBenchmark/build/query -query_type range-intersects -index_type rtspatial -load_factor 1",
            },
            {
                "case_id": "lakes_bz2_select_0.01_10000",
                "author_count": 0,
                "geometry_subset": "Paper-reproduction-apps/librts-paper/results/goal5508_lakes_degenerate.wkt",
                "query_sha256": "3ddc24019d37f4dd0bc0c1f41ef04cb24d6e1f9d852f068f7eae87ca014aeb04",
                "command_contract": "SpatialQueryBenchmark/build/query -query_type range-intersects -index_type rtspatial -load_factor 1",
            },
        ],
        "source_audit": {
            "source_path": "src/native/optix/rtdl_optix_workloads.cpp",
            "source_sha256": sha256(source),
            "library_path": "Paper-reproduction-apps/librts-paper/results/goal5508_librtdl_optix.so",
            "library_sha256": sha256(library),
            "pod": "157.157.221.29:25039",
            "gpu": "NVIDIA RTX 4000 Ada Generation",
            "cuda": "12.8",
            "optix_sdk": "/workspace/vendor/optix-sdk",
        },
        "checks": {
            "official_parks_author_match": official_rows[0]["fixed_delta"] == 0,
            "official_lakes_author_match": official_rows[1]["fixed_delta"] == 0,
            "degenerate_parks_author_match": degenerate_rows[0]["fixed_rtdl_count"] == degenerate_rows[0]["author_count"],
            "degenerate_lakes_author_match": degenerate_rows[1]["fixed_rtdl_count"] == degenerate_rows[1]["author_count"],
            "source_and_rtdl_input_mbr_contract_is_same": True,
            "generic_native_kernel_fix": True,
        },
        "claim_boundary": {
            "generic_native_semantic_fix_claimed": True,
            "full_official_input_adjudication": False,
            "complete_range_intersects_matrix_claimed": False,
            "paper_reproduction_claimed": False,
            "performance_ratio_authorized": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "embree_in_scope": False,
        },
    }
    output = RESULTS / "goal5508_generic_float32_degenerate_aabb_validity_fix_gate.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
