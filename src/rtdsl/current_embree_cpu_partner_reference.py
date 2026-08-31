from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION = (
    "rtdl.v2_11.current_embree_cpu_partner_reference.goal4308.v1"
)
CURRENT_EMBREE_CPU_PARTNER_REFERENCE_STATUS = (
    "internal_embree_cpu_partner_reference_not_release_authorization"
)
CURRENT_EMBREE_CPU_PARTNER_REFERENCE_CLAIM_BOUNDARY = (
    "Goal4298 records the v2.11 Embree CPU plus current CPU partner reference "
    "packet for the ten current benchmark apps. It does not authorize release "
    "action, package-install wording, public speedup wording, whole-app "
    "acceleration wording, broad RT-core wording, NVIDIA/AMD/Intel GPU "
    "performance wording, paper-reproduction wording, true-zero-copy wording, "
    "automatic partner selection, or app-specific native-engine logic."
)


@dataclass(frozen=True)
class CurrentEmbreeCpuPartnerReference:
    app: str
    row_id: str
    purpose: str
    route_class: str
    command: tuple[str, ...]
    timeout_sec: int
    evidence_refs: tuple[str, ...]
    uses_embree: bool
    uses_numba: bool = False
    requires_embree_library: bool = True
    requires_numba: bool = False
    cpu_thread_policy: str = "runner_sets_all_thread_cpu_env"
    result_contract: str = "stdout_json_with_no_claim_authorization"
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False
    intel_gpu_performance_claim_authorized: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown promoted benchmark app: {self.app}")
        if self.route_class not in {
            "embree_cpu_rt_primitive",
            "embree_cpu_rt_plus_python_continuation",
            "embree_cpu_rt_plus_numba_reference",
        }:
            raise ValueError(f"{self.app}: unknown route_class {self.route_class!r}")
        if not self.row_id or not self.purpose:
            raise ValueError(f"{self.app}: row_id and purpose must be explicit")
        if not self.command or self.command[0] not in {"python", "py"}:
            raise ValueError(f"{self.app}: command must start with python or py")
        if self.timeout_sec <= 0:
            raise ValueError(f"{self.app}: timeout_sec must be positive")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence_refs must not be empty")
        if self.uses_embree != self.requires_embree_library:
            raise ValueError(f"{self.app}: Embree usage and library requirement must agree")
        if self.uses_numba and not self.requires_numba:
            raise ValueError(f"{self.app}: Numba usage must require Numba")
        if self.requires_numba and not self.uses_numba:
            raise ValueError(f"{self.app}: Numba requirement must be tied to usage")
        if self.cpu_thread_policy != "runner_sets_all_thread_cpu_env":
            raise ValueError(f"{self.app}: cpu_thread_policy must stay explicit")
        if self.result_contract != "stdout_json_with_no_claim_authorization":
            raise ValueError(f"{self.app}: result_contract must preserve claim-boundary checking")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
            "intel_gpu_performance_claim_authorized",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
            "status": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_STATUS,
            "app": self.app,
            "row_id": self.row_id,
            "purpose": self.purpose,
            "route_class": self.route_class,
            "command": self.command,
            "timeout_sec": self.timeout_sec,
            "evidence_refs": self.evidence_refs,
            "uses_embree": self.uses_embree,
            "uses_numba": self.uses_numba,
            "requires_embree_library": self.requires_embree_library,
            "requires_numba": self.requires_numba,
            "cpu_thread_policy": self.cpu_thread_policy,
            "result_contract": self.result_contract,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "intel_gpu_performance_claim_authorized": self.intel_gpu_performance_claim_authorized,
            "claim_boundary": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_CLAIM_BOUNDARY,
        }


CURRENT_EMBREE_CPU_PARTNER_REFERENCE_ROWS: tuple[CurrentEmbreeCpuPartnerReference, ...] = (
    CurrentEmbreeCpuPartnerReference(
        app="hausdorff_xhd",
        row_id="hausdorff_xhd_embree_cpu_directed_summary",
        purpose="Embree CPU directed nearest-candidate summary for the Hausdorff/X-HD benchmark app",
        route_class="embree_cpu_rt_primitive",
        command=(
            "python",
            "examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
            "--backend",
            "embree",
            "--embree-result-mode",
            "directed_summary",
            "--copies",
            "8",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=120,
        evidence_refs=("Goal4298", "Goal2037"),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="spatial_rayjoin",
        row_id="spatial_rayjoin_pip_count_embree_cpu_generic_kernel",
        purpose="Embree CPU generic-kernel PIP count route for the spatial RayJoin benchmark app",
        route_class="embree_cpu_rt_plus_python_continuation",
        command=(
            "python",
            "examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
            "--workload",
            "pip",
            "--backend",
            "embree",
            "--execution-route",
            "generic_kernel",
            "--result-mode",
            "count",
            "--no-rows",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal4298", "Goal2037"),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="rt_dbscan",
        row_id="rt_dbscan_embree_cpu_prepared_rows",
        purpose="Embree CPU prepared fixed-radius row route for RT-DBSCAN compatibility coverage",
        route_class="embree_cpu_rt_plus_python_continuation",
        command=(
            "python",
            "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
            "--mode",
            "embree_prepared_rows",
            "--dataset",
            "tiny",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal4298", "Goal2627"),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="robot_collision",
        row_id="robot_collision_embree_cpu_prepared_buffers",
        purpose="Embree CPU prepared-buffer robot collision coverage route",
        route_class="embree_cpu_rt_primitive",
        command=(
            "python",
            "examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py",
            "--mode",
            "embree_prepared_buffers",
            "--dataset",
            "tiny",
            "--repeats",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal4298", "Goal2037"),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="contact_manifold",
        row_id="contact_manifold_embree_cpu_native_collect_k",
        purpose="Embree CPU bounded collect-k route for contact-manifold witness coverage",
        route_class="embree_cpu_rt_primitive",
        command=(
            "python",
            "examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
            "--mode",
            "native_collect_k",
            "--backend",
            "embree",
            "--dataset",
            "tiny",
            "--witness-capacity",
            "8",
            "--repeat-count",
            "2",
        ),
        timeout_sec=120,
        evidence_refs=("Goal4298",),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="raydb_style",
        row_id="raydb_style_embree_cpu_count_primitive_first",
        purpose="Embree CPU primitive-first grouped count route for RayDB-style columnar payloads",
        route_class="embree_cpu_rt_primitive",
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
            "4096",
            "--generated-groups",
            "128",
            "--repeat",
            "2",
            "--warmup",
            "1",
            "--summary-only-iterations",
        ),
        timeout_sec=180,
        evidence_refs=("Goal4298", "Goal2979"),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="barnes_hut",
        row_id="barnes_hut_embree_cpu_node_coverage_prepared",
        purpose="Embree CPU prepared node-coverage route for Barnes-Hut candidate coverage",
        route_class="embree_cpu_rt_plus_python_continuation",
        command=(
            "python",
            "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
            "--mode",
            "embree_node_coverage_prepared",
            "--body-count",
            "1024",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal4298", "Goal2037"),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="librts_spatial_index",
        row_id="librts_spatial_index_embree_cpu_aabb_index",
        purpose="Embree CPU AABB-index route for the LibRTS-style spatial-index benchmark",
        route_class="embree_cpu_rt_primitive",
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
        ),
        timeout_sec=180,
        evidence_refs=("Goal4298",),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="rtnn",
        row_id="rtnn_embree_cpu_ann_candidate_quality_reference",
        purpose="Embree CPU candidate-quality route for the RTNN benchmark app's 2-D ANN contract",
        route_class="embree_cpu_rt_plus_python_continuation",
        command=(
            "python",
            "examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py",
            "--mode",
            "ann_embree_quality",
            "--copies",
            "128",
        ),
        timeout_sec=180,
        evidence_refs=("Goal4308", "Goal4298", "Goal3820"),
        uses_embree=True,
    ),
    CurrentEmbreeCpuPartnerReference(
        app="triangle_counting",
        row_id="triangle_counting_embree_cpu_native_summary",
        purpose="Embree CPU native graph-summary route for triangle counting",
        route_class="embree_cpu_rt_primitive",
        command=(
            "python",
            "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
            "--mode",
            "run",
            "--backend",
            "embree",
            "--output-mode",
            "summary",
            "--copies",
            "128",
            "--partner",
            "none",
            "--repeat",
            "2",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal4298", "Goal3819"),
        uses_embree=True,
    ),
)


def current_embree_cpu_partner_reference_rows() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in CURRENT_EMBREE_CPU_PARTNER_REFERENCE_ROWS)


def summarize_current_embree_cpu_partner_reference(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_embree_cpu_partner_reference_rows()
    return {
        "version": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
        "status": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_STATUS,
        "app_count": len({row["app"] for row in matrix}),
        "row_count": len(matrix),
        "embree_rows": tuple(row["row_id"] for row in matrix if row["uses_embree"]),
        "numba_rows": tuple(row["row_id"] for row in matrix if row["uses_numba"]),
        "requires_embree_library_rows": tuple(
            row["row_id"] for row in matrix if row["requires_embree_library"]
        ),
        "requires_numba_rows": tuple(row["row_id"] for row in matrix if row["requires_numba"]),
        "claim_boundary": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_CLAIM_BOUNDARY,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "intel_gpu_performance_claim_authorized": False,
    }


def validate_current_embree_cpu_partner_reference(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_embree_cpu_partner_reference_rows()
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
        command_text = " ".join(command) if isinstance(command, tuple) else ""
        if not isinstance(command, tuple) or not command:
            errors.append(f"{app}: command must be a non-empty tuple")
        if "optix" in command_text.lower():
            errors.append(f"{app}: Embree CPU reference command must not route through OptiX")
        if "cupy" in command_text.lower():
            errors.append(f"{app}: Embree CPU reference command must not route through CuPy")
        if "--require-rt-core" in command_text:
            errors.append(f"{app}: Embree CPU reference command must not require RT cores")
        if not row.get("purpose"):
            errors.append(f"{app}: purpose must be explicit")
        if not row.get("evidence_refs"):
            errors.append(f"{app}: evidence_refs must be non-empty")
        if not isinstance(row.get("timeout_sec"), int) or int(row.get("timeout_sec", 0)) <= 0:
            errors.append(f"{app}: timeout_sec must be positive")
        if bool(row.get("uses_embree")) != bool(row.get("requires_embree_library")):
            errors.append(f"{app}: uses_embree and requires_embree_library must agree")
        if bool(row.get("uses_numba")) != bool(row.get("requires_numba")):
            errors.append(f"{app}: uses_numba and requires_numba must agree")
        if not row.get("uses_embree"):
            errors.append(f"{app}: benchmark rows must exercise Embree CPU")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
            "intel_gpu_performance_claim_authorized",
        ):
            if row.get(flag):
                errors.append(f"{app}: {flag} must remain false")
    return {
        "version": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "row_count": len(matrix),
        "claim_boundary": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_CLAIM_BOUNDARY,
    }
