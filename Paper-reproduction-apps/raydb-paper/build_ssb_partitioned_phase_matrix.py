from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from statistics import median
from typing import Sequence


QUERY_IDS = (
    "q11", "q12", "q13", "q21", "q22", "q23", "q31",
    "q32", "q33", "q34", "q41", "q42", "q43",
)
AUTHOR_TIMING_PATTERN = re.compile(
    r"\[Time\] Build BVH: (?P<build>[0-9.]+) ms.*?"
    r"\[Time\] Launch\(Prepare included\): (?P<prepare>[0-9.]+) ms.*?"
    r"\[Time\] Launch: (?P<launch>[0-9.]+) ms",
    re.DOTALL,
)


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_author_timings(payload: dict[str, object]) -> dict[str, float]:
    match = AUTHOR_TIMING_PATTERN.search(str(payload.get("raw_stdout", "")))
    if match is None:
        raise ValueError("author result does not contain Build/Launch timing lines")
    return {
        "build_bvh_ms": float(match.group("build")),
        "launch_prepare_included_ms": float(match.group("prepare")),
        "launch_ms": float(match.group("launch")),
    }


def build_summary(
    *,
    evidence_root: Path,
    matrix_path: Path,
    scale_factor: int,
    host_label: str,
    gpu_label: str,
) -> dict[str, object]:
    matrix = _read_json(matrix_path)
    if matrix.get("schema") != "rtdl.paper_reproduction.raydb.generated_ssb_partitioned_matrix.v3":
        raise ValueError("partitioned matrix must use the identity-locked v3 evidence schema")
    if int(matrix.get("scale_factor", -1)) != int(scale_factor):
        raise ValueError("partitioned matrix scale factor mismatch")

    execution_identity = matrix.get("execution_identity")
    if not isinstance(execution_identity, dict):
        raise ValueError("partitioned matrix lacks its execution cohort identity")
    if execution_identity.get("host") != host_label:
        raise ValueError("matrix execution identity host mismatch")
    if execution_identity.get("gpu_identity") != gpu_label:
        raise ValueError("matrix execution identity GPU mismatch")
    matrix_cases = {
        str(case.get("query_id")): case
        for case in matrix.get("cases", [])
        if isinstance(case, dict)
    }

    cases: list[dict[str, object]] = []
    for query_id in QUERY_IDS:
        author_path = evidence_root / f"goal5562_sf{scale_factor}_{query_id}_author.json"
        rtdl_path = evidence_root / f"goal5562_sf{scale_factor}_{query_id}_rtdl_partitioned.json"
        author = _read_json(author_path)
        rtdl = _read_json(rtdl_path)
        if author.get("schema") != "rtdl.paper_reproduction.raydb.author_packet_gate.v2":
            raise ValueError(f"{query_id} author evidence is not v2")
        if rtdl.get("schema") != "rtdl.paper_reproduction.raydb.ssb_packet_rtdl_gate.v3":
            raise ValueError(f"{query_id} RTDL evidence is not v3")
        if rtdl.get("host") != host_label:
            raise ValueError(f"{query_id} RTDL host does not match the matrix execution host")
        matrix_case = matrix_cases.get(query_id)
        if not isinstance(matrix_case, dict) or matrix_case.get("passed") is not True:
            raise ValueError(f"{query_id} did not pass the identity-locked matrix gate")
        evidence_bundle = matrix_case.get("evidence_bundle")
        if not isinstance(evidence_bundle, dict):
            raise ValueError(f"{query_id} matrix case lacks its evidence bundle")
        if (
            _sha256_file(author_path) != evidence_bundle.get("author_result_sha256")
            or _sha256_file(rtdl_path) != evidence_bundle.get("rtdl_result_sha256")
        ):
            raise ValueError(f"{query_id} child evidence changed after matrix validation")
        expected_child_identity = {
            "evidence_cohort_id": execution_identity.get("evidence_cohort_id"),
            "host": execution_identity.get("host"),
            "gpu_identity": execution_identity.get("gpu_identity"),
            "matrix_runner_sha256": execution_identity.get("matrix_runner_sha256"),
        }
        identity_verified = bool(
            author.get("execution_identity") == expected_child_identity
            and rtdl.get("execution_identity") == expected_child_identity
            and matrix_case.get("author_execution_identity_verified") is True
            and matrix_case.get("rtdl_execution_identity_verified") is True
            and matrix_case.get("same_execution_cohort_verified") is True
        )
        if not identity_verified:
            raise ValueError(f"{query_id} author/RTDL execution identity mismatch")
        correctness = bool(
            author.get("author_matches_cpu_oracle") is True
            and rtdl.get("author_matches_oracle") is True
            and rtdl.get("rtdl_matches_oracle") is True
            and rtdl.get("author_matches_rtdl") is True
            and rtdl.get("same_packet_bytes_as_author") is True
            and author.get("packet_files_stable_during_author_run") is True
            and not rtdl.get("missing_rows")
            and not rtdl.get("unexpected_rows")
        )
        timing_denominators = rtdl.get("timing_denominators")
        if not isinstance(timing_denominators, dict) or (
            not isinstance(timing_denominators.get("nesting_graph"), dict)
            or timing_denominators["nesting_graph"].get("schema")
            != "rtdl.timing.nesting_graph.v1"
        ):
            raise ValueError(f"{query_id} lacks the timing nesting graph")
        phase = rtdl.get("phase_timing_seconds")
        if not isinstance(phase, dict):
            raise ValueError(f"{query_id} lacks phase timings")
        author_ms = parse_author_timings(author)
        rtdl_launch_ms = float(phase["launch"]) * 1000.0
        if rtdl_launch_ms <= 0.0:
            raise ValueError(f"{query_id} RTDL launch time must be positive")
        partition_count = int(rtdl.get("partition_count", 0))
        cases.append(
            {
                "query_id": query_id,
                "input_identity_level": rtdl.get("input_identity_level"),
                "correctness_and_identity_gate_passed": correctness,
                "execution_identity_verified": identity_verified,
                "child_artifact_hashes_verified": True,
                "same_host": rtdl.get("host") == host_label,
                "same_host_evidence": (
                    "author and RTDL evidence carry the same persistent cohort id, exact host, "
                    "GPU identity, matrix-runner hash, and code/native hashes; a resumed cohort "
                    "may span outer-runner process invocations"
                ),
                "same_packet_hashes": rtdl.get("same_packet_bytes_as_author") is True,
                "author_packet_stable": author.get("packet_files_stable_during_author_run") is True,
                "author_launch_topology": "one monolithic launch",
                "rtdl_launch_topology": f"{partition_count} sequential partition launches",
                "same_launch_topology": partition_count == 1,
                "partition_count": partition_count,
                "author_ms": author_ms,
                "rtdl_ms": {
                    "app_lowering": float(phase["app_lowering"]) * 1000.0,
                    "host_pack_rays_only": float(phase["host_pack_rays_only"]) * 1000.0,
                    "route_total_including_partition_triangle_pack": float(
                        phase["route_total_including_partition_triangle_pack"]
                    ) * 1000.0,
                    "prepare_build": float(phase["prepare_build"]) * 1000.0,
                    "prepared_ray_batch_prepare": float(
                        phase["prepared_ray_batch_prepare"]
                    ) * 1000.0,
                    "primitive_payload_prepare": float(
                        phase["primitive_payload_prepare"]
                    ) * 1000.0,
                    "query_prepare_native": float(phase["query_prepare_native"]) * 1000.0,
                    "launch": rtdl_launch_ms,
                    "result_download": float(phase["result_download"]) * 1000.0,
                },
                "author_launch_over_rtdl_partitioned_launch_sum": (
                    author_ms["launch_ms"] / rtdl_launch_ms
                ),
                "ratio_scope": (
                    "same_host_same_packet_same_launch_plus_sync_phase__"
                    "different_monolithic_vs_partitioned_launch_topology"
                ),
                "timing_denominators": timing_denominators,
            }
        )

    all_passed = all(
        case["correctness_and_identity_gate_passed"]
        and case["execution_identity_verified"]
        for case in cases
    )
    ratios = [float(case["author_launch_over_rtdl_partitioned_launch_sum"]) for case in cases]
    author_launch = [float(case["author_ms"]["launch_ms"]) for case in cases]
    rtdl_launch = [float(case["rtdl_ms"]["launch"]) for case in cases]
    input_identity_levels = {case["input_identity_level"] for case in cases}
    if len(input_identity_levels) != 1:
        raise ValueError("per-query input identity levels are inconsistent")
    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_partitioned_phase_matrix.v2",
        "scale_factor": scale_factor,
        "host": host_label,
        "gpu": gpu_label,
        "execution_identity": execution_identity,
        "input_identity_level": next(iter(input_identity_levels)),
        "query_count": len(cases),
        "all_correctness_and_identity_gates_passed": all_passed,
        "phase_contract": {
            "author_launch": "author-reported optixLaunch plus synchronization only",
            "rtdl_launch": "sum of per-partition optixLaunch plus synchronization only",
            "phase_boundary_aligned": True,
            "launch_topology_aligned": all(case["same_launch_topology"] for case in cases),
            "interpretation": (
                "The launch phase denominator is aligned, but the author uses one monolithic launch "
                "and RTDL uses bounded sequential partitions. Ratios describe this operational phase "
                "on one host; they are not algorithm parity or paper performance."
            ),
        },
        "launch_only_summary": {
            "author_launch_median_ms": median(author_launch),
            "rtdl_partitioned_launch_sum_median_ms": median(rtdl_launch),
            "per_query_author_over_rtdl_ratio_median": median(ratios),
            "per_query_author_over_rtdl_ratio_min": min(ratios),
            "per_query_author_over_rtdl_ratio_max": max(ratios),
            "rtdl_faster_query_count": sum(value > 1.0 for value in ratios),
            "author_faster_query_count": sum(value < 1.0 for value in ratios),
            "tie_query_count": sum(value == 1.0 for value in ratios),
            "cross_query_aggregate_speedup_authorized": False,
        },
        "cases": cases,
        "decision": {
            "same_host_same_packet_launch_phase_ratios_authorized": all_passed,
            "same_launch_topology_ratio_claimed": False,
            "figure12_ratio_authorized": False,
            "paper_hardware_ratio_authorized": False,
            "whole_program_ratio_authorized": False,
            "paper_performance_claimed": False,
        },
        "claim_boundary": {
            "generated_same_source_sf_matrix_claimed": all_passed,
            "exact_paper_input_claimed": False,
            "author_algorithm_equivalence_claimed": False,
            "figure12_reproduced": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a denominator-explicit RayDB partitioned launch-phase matrix"
    )
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--matrix-json", type=Path, required=True)
    parser.add_argument("--scale-factor", type=int, required=True)
    parser.add_argument("--host-label", required=True)
    parser.add_argument("--gpu-label", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    summary = build_summary(
        evidence_root=args.evidence_root,
        matrix_path=args.matrix_json,
        scale_factor=args.scale_factor,
        host_label=args.host_label,
        gpu_label=args.gpu_label,
    )
    _write_json_atomic(args.output_json, summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["all_correctness_and_identity_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
