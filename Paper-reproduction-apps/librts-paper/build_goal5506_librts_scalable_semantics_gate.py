from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SCHEMA = "rtdl.paper_reproduction.librts.goal5506_scalable_semantics_gate.v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--author-stdout", type=Path, required=True)
    parser.add_argument("--rtdl", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    oracle = json.loads(args.oracle.read_text(encoding="utf-8"))
    rtdl = json.loads(args.rtdl.read_text(encoding="utf-8"))
    author_text = args.author_stdout.read_text(encoding="utf-8")
    matches = re.findall(r"Results\s+(\d+)", author_text)
    if not matches:
        raise ValueError("author output has no Results count")
    author_count = int(matches[-1])
    rtdl_count = int(rtdl["result_count"])
    cpu_count = int(oracle["cpu_inclusive_count"])
    source_count = int(oracle["source_rayparams_model_count"])
    payload = {
        "schema": SCHEMA,
        "status": "scalable_runtime_semantics_gate_completed",
        "input_identity": {
            "seed": oracle["seed"],
            "geometry_count": oracle["geometry_count"],
            "query_count": oracle["query_count"],
            "pair_count": oracle["pair_count"],
            "geometry_sha256": sha256(args.geometry),
            "query_sha256": sha256(args.query),
            "same_input_author_and_rtdl": True,
        },
        "counts": {
            "cpu_inclusive_oracle": cpu_count,
            "source_rayparams_model": source_count,
            "author_gpu_runtime": author_count,
            "rtdl_optix_runtime": rtdl_count,
        },
        "phase_observations": {
            "author_loading_ms": None,
            "author_query_ms_internal": None,
            "rtdl_prepare_sec": rtdl.get("prepare_sec"),
            "rtdl_query_wall_sec": rtdl.get("query_wall_sec"),
            "rtdl_primitive_query_sec": rtdl.get("primitive_query_sec"),
            "performance_ratio_authorized": False,
        },
        "classification": {
            "author_matches_source_model": author_count == source_count,
            "rtdl_matches_cpu_inclusive_oracle": rtdl_count == cpu_count,
            "author_rtdl_counts_match": author_count == rtdl_count,
            "source_model_explains_author_count": author_count == source_count,
            "rtdl_generic_contract_matches_cpu_oracle": rtdl_count == cpu_count,
        },
        "claim_boundary": {
            "scalable_probe_only": True,
            "full_input_adjudication": False,
            "full_input_root_cause_resolved": False,
            "rtdl_core_change_authorized": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "performance_ratio_authorized": False,
            "paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
