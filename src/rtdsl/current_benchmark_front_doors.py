from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


CURRENT_BENCHMARK_FRONT_DOOR_VERSION = "rtdl.v2_10.current_benchmark_front_doors.goal3823.v1"
CURRENT_BENCHMARK_FRONT_DOOR_STATUS = "internal_command_registry_not_release_authorization"
CURRENT_BENCHMARK_FRONT_DOOR_CLAIM_BOUNDARY = (
    "Goal3823 records the current executable benchmark app front-door commands "
    "after Goals3818-3822. It does not authorize release action, package-install "
    "wording, public speedup wording, whole-app acceleration wording, broad RT-core "
    "wording, paper-reproduction wording, true-zero-copy wording, AMD performance "
    "wording, automatic partner selection, or app-specific native-engine logic."
)


@dataclass(frozen=True)
class CurrentBenchmarkFrontDoor:
    app: str
    row_id: str
    purpose: str
    command: tuple[str, ...]
    timeout_sec: int
    evidence_refs: tuple[str, ...]
    requires_optix_library: bool = True
    requires_numba: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown promoted benchmark app: {self.app}")
        if not self.row_id or not self.purpose:
            raise ValueError(f"{self.app}: row_id and purpose must be explicit")
        if not self.command or self.command[0] not in {"python", "py"}:
            raise ValueError(f"{self.app}: command must start with python or py")
        if self.timeout_sec <= 0:
            raise ValueError(f"{self.app}: timeout_sec must be positive")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence_refs must not be empty")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": CURRENT_BENCHMARK_FRONT_DOOR_VERSION,
            "status": CURRENT_BENCHMARK_FRONT_DOOR_STATUS,
            "app": self.app,
            "row_id": self.row_id,
            "purpose": self.purpose,
            "command": self.command,
            "timeout_sec": self.timeout_sec,
            "evidence_refs": self.evidence_refs,
            "requires_optix_library": self.requires_optix_library,
            "requires_numba": self.requires_numba,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": CURRENT_BENCHMARK_FRONT_DOOR_CLAIM_BOUNDARY,
        }


CURRENT_BENCHMARK_FRONT_DOORS: tuple[CurrentBenchmarkFrontDoor, ...] = (
    CurrentBenchmarkFrontDoor(
        app="hausdorff_xhd",
        row_id="hausdorff_xhd_current_optix_threshold",
        purpose="current Hausdorff/X-HD style OptiX threshold front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
            "--backend",
            "optix",
            "--require-rt-core",
            "--optix-summary-mode",
            "directed_threshold_prepared",
            "--hausdorff-threshold",
            "0.25",
            "--copies",
            "8",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=120,
        evidence_refs=("Goal3818",),
    ),
    CurrentBenchmarkFrontDoor(
        app="spatial_rayjoin",
        row_id="spatial_rayjoin_pip_count_current_prepared_optix",
        purpose="current RayJoin-style prepared OptiX PIP count front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
            "--workload",
            "pip",
            "--backend",
            "optix",
            "--execution-route",
            "prepared_optix",
            "--result-mode",
            "count",
            "--pip-count-mode",
            "device_filtered_prepared_points_validated",
            "--no-rows",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3818", "Goal3761"),
    ),
    CurrentBenchmarkFrontDoor(
        app="rt_dbscan",
        row_id="rt_dbscan_optix_numba_prepared_grid",
        purpose="current RT-DBSCAN OptiX threshold flags plus Numba component continuation",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
            "--mode",
            "optix_rt_core_flags_numba_prepared_grid_components_3d",
            "--dataset",
            "clustered3d",
            "--point-count",
            "4096",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3818", "Goal3758"),
        requires_numba=True,
    ),
    CurrentBenchmarkFrontDoor(
        app="robot_collision",
        row_id="robot_collision_optix_prepared_device_count",
        purpose="current robot-collision prepared OptiX device-count front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py",
            "--mode",
            "optix_prepared_device_count",
            "--dataset",
            "scaled",
            "--pose-count",
            "256",
            "--obstacle-count",
            "64",
            "--link-count",
            "4",
            "--repeats",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3818", "Goal3757"),
    ),
    CurrentBenchmarkFrontDoor(
        app="contact_manifold",
        row_id="contact_manifold_optix_native_collect_k",
        purpose="current contact-manifold bounded collect-k front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
            "--mode",
            "native_collect_k",
            "--backend",
            "optix",
            "--dataset",
            "grid",
            "--grid-count",
            "16",
            "--witness-capacity",
            "32",
            "--repeat-count",
            "2",
        ),
        timeout_sec=120,
        evidence_refs=("Goal3818",),
    ),
    CurrentBenchmarkFrontDoor(
        app="raydb_style",
        row_id="raydb_style_optix_count_primitive_first",
        purpose="current RayDB-style primitive-first grouped count front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py",
            "--mode",
            "count",
            "--backend",
            "paper_rt_optix_v2_5_primitive_first",
            "--fixture-kind",
            "generated",
            "--generated-rows",
            "4096",
            "--generated-groups",
            "128",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3818",),
    ),
    CurrentBenchmarkFrontDoor(
        app="barnes_hut",
        row_id="barnes_hut_numba_exact_force",
        purpose="current Barnes-Hut no-RawKernel Numba exact-force front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
            "--mode",
            "partner_exact_force",
            "--partner",
            "numba",
            "--body-count",
            "1024",
            "--skip-validation",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3818", "Goal3762"),
        requires_numba=True,
    ),
    CurrentBenchmarkFrontDoor(
        app="librts_spatial_index",
        row_id="librts_spatial_index_optix_aabb_index",
        purpose="current LibRTS-style prepared OptiX AABB-index front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
            "--mode",
            "optix_aabb_index",
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
        ),
        timeout_sec=180,
        evidence_refs=("Goal3818",),
    ),
    CurrentBenchmarkFrontDoor(
        app="rtnn",
        row_id="rtnn_prepared_optix_ranked_summary",
        purpose="current RTNN prepared OptiX ranked-summary executable front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py",
            "--mode",
            "prepared_optix_ranked_summary",
            "--point-count",
            "4096",
            "--radius",
            "0.02",
            "--k",
            "32",
            "--repeat",
            "2",
            "--query-batch-size",
            "4096",
            "--distribution",
            "uniform",
        ),
        timeout_sec=120,
        evidence_refs=("Goal3820",),
    ),
    CurrentBenchmarkFrontDoor(
        app="triangle_counting",
        row_id="triangle_counting_optix_native_summary",
        purpose="current triangle-counting explicit native timing front door",
        command=(
            "python",
            "examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
            "--mode",
            "run",
            "--backend",
            "optix",
            "--output-mode",
            "summary",
            "--optix-graph-mode",
            "native",
            "--copies",
            "128",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3819",),
    ),
)


def current_benchmark_front_doors() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in CURRENT_BENCHMARK_FRONT_DOORS)


def summarize_current_benchmark_front_doors(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_benchmark_front_doors()
    return {
        "version": CURRENT_BENCHMARK_FRONT_DOOR_VERSION,
        "status": CURRENT_BENCHMARK_FRONT_DOOR_STATUS,
        "app_count": len({row["app"] for row in matrix}),
        "row_count": len(matrix),
        "numba_required_rows": tuple(row["row_id"] for row in matrix if row["requires_numba"]),
        "optix_required_rows": tuple(row["row_id"] for row in matrix if row["requires_optix_library"]),
        "claim_boundary": CURRENT_BENCHMARK_FRONT_DOOR_CLAIM_BOUNDARY,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def validate_current_benchmark_front_doors(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_benchmark_front_doors()
    errors: list[str] = []
    apps = {row.get("app") for row in matrix}
    expected_apps = set(V2_8_PROMOTED_BENCHMARK_APPS)
    if apps != expected_apps:
        errors.append(f"app coverage mismatch: got={sorted(apps)} expected={sorted(expected_apps)}")
    row_ids = [str(row.get("row_id", "")) for row in matrix]
    if len(row_ids) != len(set(row_ids)):
        errors.append("row_id values must be unique")
    for row in matrix:
        app = str(row.get("app", "<missing>"))
        command = row.get("command")
        if not isinstance(command, tuple) or not command:
            errors.append(f"{app}: command must be a non-empty tuple")
        if not row.get("purpose"):
            errors.append(f"{app}: purpose must be explicit")
        if not row.get("evidence_refs"):
            errors.append(f"{app}: evidence_refs must be non-empty")
        if not isinstance(row.get("timeout_sec"), int) or int(row.get("timeout_sec", 0)) <= 0:
            errors.append(f"{app}: timeout_sec must be positive")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{app}: {flag} must remain false")
    return {
        "version": CURRENT_BENCHMARK_FRONT_DOOR_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "row_count": len(matrix),
        "claim_boundary": CURRENT_BENCHMARK_FRONT_DOOR_CLAIM_BOUNDARY,
    }
