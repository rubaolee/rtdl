from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .current_benchmark_scale_profiles import CURRENT_BENCHMARK_SCALE_PROFILE_VERSION
from .optimized_optix_embree_comparison_packet import optimized_optix_embree_comparison_packet


CPU_ONLY_POD_COMPARISON_LAUNCH_VERSION = "rtdl.v2_12.cpu_only_pod_comparison_launch.goal4364.v1"
CPU_ONLY_POD_COMPARISON_LAUNCH_STATUS = (
    "internal_cpu_only_optix_vs_embree_pod_launch_packet_not_release_authorization"
)
CPU_ONLY_POD_COMPARISON_LAUNCH_CLAIM_BOUNDARY = (
    "Goal4346 is a CPU-only OptiX-vs-Embree launch packet. It targets NVIDIA "
    "RT-core OptiX rows versus Embree CPU rows only. It has no Intel-GPU lane "
    "and does not authorize release action, public speedup wording, whole-app "
    "acceleration wording, broad RT-core wording, paper reproduction wording, "
    "true-zero-copy wording, automatic partner selection, or app-specific "
    "native-engine logic."
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = "docs/reports/goal4346_cpu_only_pod_comparison_run"


@dataclass(frozen=True)
class EmbreeCpuScaleCommand:
    app: str
    bucket: str
    command: tuple[str, ...]
    output_json: str
    timeout_sec: int
    note: str

    def to_metadata(self) -> dict[str, Any]:
        return {
            "app": self.app,
            "bucket": self.bucket,
            "command": self.command,
            "output_json": self.output_json,
            "timeout_sec": self.timeout_sec,
            "note": self.note,
            "requires_embree_library": True,
            "requires_nvidia_rt_core": False,
            "requires_intel_gpu": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
        }


EMBREE_CPU_SCALE_COMMANDS: tuple[EmbreeCpuScaleCommand, ...] = (
    EmbreeCpuScaleCommand(
        app="hausdorff_xhd",
        bucket="clean_internal_query_ratio",
        command=(
            "python",
            "examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
            "--backend",
            "embree",
            "--optix-summary-mode",
            "directed_threshold_prepared",
            "--hausdorff-threshold",
            "0.25",
            "--copies",
            "1024",
            "--repeat",
            "5",
            "--warmup",
            "1",
        ),
        output_json=f"{OUTPUT_ROOT}/embree_scale_outputs/hausdorff_xhd.json",
        timeout_sec=180,
        note="Same threshold-decision contract as the current OptiX scale row.",
    ),
    EmbreeCpuScaleCommand(
        app="robot_collision",
        bucket="clean_internal_query_ratio",
        command=(
            "python",
            "examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py",
            "--mode",
            "embree_prepared_buffers",
            "--dataset",
            "scaled",
            "--pose-count",
            "1024",
            "--obstacle-count",
            "128",
            "--link-count",
            "4",
            "--repeats",
            "50000",
            "--warmup",
            "100",
            "--no-probe-reference",
            "--summary-only-runs",
        ),
        output_json=f"{OUTPUT_ROOT}/embree_scale_outputs/robot_collision.json",
        timeout_sec=360,
        note="Same prepared-buffer compact flag contract as the Goal4363 OptiX pair.",
    ),
    EmbreeCpuScaleCommand(
        app="contact_manifold",
        bucket="clean_internal_query_ratio",
        command=(
            "python",
            "examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
            "--mode",
            "native_collect_k",
            "--backend",
            "embree",
            "--dataset",
            "grid",
            "--grid-count",
            "64",
            "--witness-capacity",
            "128",
            "--repeat-count",
            "3",
        ),
        output_json=f"{OUTPUT_ROOT}/embree_scale_outputs/contact_manifold.json",
        timeout_sec=180,
        note="Same collect-k grid, capacity, and repeat policy as OptiX.",
    ),
    EmbreeCpuScaleCommand(
        app="raydb_style",
        bucket="clean_internal_query_ratio",
        command=(
            "python",
            "examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py",
            "--mode",
            "count",
            "--backend",
            "paper_rt_embree",
            "--fixture-kind",
            "generated",
            "--generated-rows",
            "262144",
            "--generated-groups",
            "1024",
            "--repeat",
            "9",
            "--warmup",
            "1",
            "--summary-only-iterations",
        ),
        output_json=f"{OUTPUT_ROOT}/embree_scale_outputs/raydb_style.json",
        timeout_sec=240,
        note="Same prepared grouped-reduction contract and repeat/warmup policy as the Goal4364 OptiX pair.",
    ),
    EmbreeCpuScaleCommand(
        app="librts_spatial_index",
        bucket="fully_optimized_measured_pair",
        command=(
            "python",
            "examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
            "--mode",
            "embree_aabb_index",
            "--dataset",
            "uniform",
            "--box-count",
            "1024",
            "--query-count",
            "1024",
            "--operation",
            "all",
            "--repeat",
            "2",
            "--warmup",
            "1",
            "--skip-counts",
        ),
        output_json=f"{OUTPUT_ROOT}/embree_scale_outputs/librts_spatial_index.json",
        timeout_sec=180,
        note="Goal4340 optimized native Embree AABB_INDEX_QUERY_2D comparison shape.",
    ),
    EmbreeCpuScaleCommand(
        app="triangle_counting",
        bucket="clean_internal_query_ratio",
        command=(
            "python",
            "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
            "--mode",
            "rt_graph_2a1_generic_rt",
            "--backend",
            "embree",
            "--fixture",
            "degree_oriented_two_triangles",
            "--rt-graph-copies",
            "2048",
            "--detail",
            "summary",
            "--repeat",
            "3",
            "--warmup",
            "1",
        ),
        output_json=f"{OUTPUT_ROOT}/embree_scale_outputs/triangle_counting.json",
        timeout_sec=240,
        note="Same RT-Graph 2A1 fixture and repeat policy as OptiX.",
    ),
)


CONTRACT_CHOICE_BLOCKERS: tuple[dict[str, str], ...] = ()


def _env_prefix() -> tuple[str, ...]:
    return (
        "export PYTHONPATH=src:.",
        "export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so",
        "export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so",
        "export RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so",
        "export RTDL_CUDA_PREFIX=${RTDL_CUDA_PREFIX:-/usr/local/cuda-12.8}",
        "export NUMBA_CUDA_PREFIX=${NUMBA_CUDA_PREFIX:-/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc}",
        "export CUDA_HOME=$NUMBA_CUDA_PREFIX",
        "export CUDA_PATH=$NUMBA_CUDA_PREFIX",
        "export PATH=$RTDL_CUDA_PREFIX/bin:$NUMBA_CUDA_PREFIX/bin:$PATH",
        "export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:$RTDL_CUDA_PREFIX/targets/x86_64-linux/lib:$RTDL_CUDA_PREFIX/lib64:${LD_LIBRARY_PATH:-}",
        "export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}",
        "export TBB_NUM_THREADS=${TBB_NUM_THREADS:-8}",
        "export MKL_NUM_THREADS=${MKL_NUM_THREADS:-8}",
        "export OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-8}",
        "export NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS:-8}",
        "export RTDL_EMBREE_THREADS=${RTDL_EMBREE_THREADS:-8}",
    )


def cpu_only_pod_comparison_launch_packet() -> dict[str, Any]:
    comparison = optimized_optix_embree_comparison_packet()
    comparison_summary = dict(comparison["summary"])
    errors: list[str] = []
    if comparison.get("validation", {}).get("status") != "accept":
        errors.append("optimized comparison packet is not accept")
    if comparison_summary.get("same_contract_scale_pair_required_count") != 0:
        errors.append("comparison packet still needs same-contract scale pairs")
    if comparison_summary.get("contract_split_pair_required_count") != 0:
        errors.append("expected zero remaining contract-choice blockers")

    optix_command = (
        "python",
        "scripts/goal3828_current_benchmark_scale_profile_runner.py",
        "--output-json",
        f"{OUTPUT_ROOT}/optix_scale_summary.json",
        "--output-dir",
        f"{OUTPUT_ROOT}/optix_scale_outputs",
        "--materialize-rayjoin-public-cdb",
    )
    postprocess_commands = (
        (
            "python",
            "scripts/rtdl_optimized_optix_embree_comparison_packet.py",
            "--output-json",
            f"{OUTPUT_ROOT}/comparison_packet.json",
            "--output-markdown",
            f"{OUTPUT_ROOT}/comparison_packet.md",
        ),
        (
            "python",
            "scripts/rtdl_backend_comparison_campaign_closeout.py",
            "--output-json",
            f"{OUTPUT_ROOT}/closeout.json",
            "--output-markdown",
            f"{OUTPUT_ROOT}/closeout.md",
        ),
    )

    return {
        "version": CPU_ONLY_POD_COMPARISON_LAUNCH_VERSION,
        "status": CPU_ONLY_POD_COMPARISON_LAUNCH_STATUS,
        "claim_boundary": CPU_ONLY_POD_COMPARISON_LAUNCH_CLAIM_BOUNDARY,
        "target": "nvidia_rt_core_optix_vs_embree_cpu_only",
        "intel_gpu_lane": "omitted_by_user_until_hardware_exists",
        "requires": {
            "nvidia_rt_core_pod_for_optix": True,
            "embree_cpu_library": True,
            "intel_gpu": False,
            "reject_non_rt_core_nvidia_gpus_for_rt_core_timing": True,
            "cuda_12_8_ptxas_first_for_numba_rows": True,
        },
        "environment_prefix": _env_prefix(),
        "optix_scale_command": {
            "scale_profile_version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
            "command": optix_command,
            "timeout_sec": 360,
            "note": "Run on an RTX-class pod. Do not use Pascal/GTX hardware for RT-core timing.",
        },
        "embree_cpu_scale_commands": tuple(row.to_metadata() for row in EMBREE_CPU_SCALE_COMMANDS),
        "contract_choice_blockers": CONTRACT_CHOICE_BLOCKERS,
        "postprocess_commands": postprocess_commands,
        "current_comparison_summary": {
            "fully_optimized_measured_pair_count": comparison_summary["measured_pair_count"],
            "fresh_scale_comparison_row_count": comparison_summary["scale_comparison_row_count"],
            "clean_internal_query_ratio_count": comparison_summary["internal_query_median_ratio_count"],
            "boundary_limited_phase_ratio_count": comparison_summary["boundary_limited_phase_ratio_count"],
            "contract_choice_blocker_count": comparison_summary["contract_split_pair_required_count"],
        },
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
    }


def validate_cpu_only_pod_comparison_launch_packet() -> dict[str, Any]:
    return cpu_only_pod_comparison_launch_packet()["validation"]
