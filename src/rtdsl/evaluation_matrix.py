from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationEntry:
    case_id: str
    workload: str
    dataset: str
    title: str
    category: str
    provenance: str
    scale_hint: int
    description: str


EMBREE_EVALUATION_MATRIX: tuple[EvaluationEntry, ...] = (
    EvaluationEntry(
        case_id="lsi_authored_minimal",
        workload="lsi",
        dataset="authored_lsi_minimal",
        title="LSI authored minimal",
        category="authored",
        provenance="Hand-authored segment example stored in baseline_runner.",
        scale_hint=2,
        description="Small sanity-check segment join with exact expected rows.",
    ),
    EvaluationEntry(
        case_id="lsi_county_slice",
        workload="lsi",
        dataset="tests/fixtures/rayjoin/br_county_subset.cdb",
        title="LSI county subset slice",
        category="fixture",
        provenance="Public RayJoin county sample reduced to the checked-in county subset fixture.",
        scale_hint=6,
        description="Deterministic county-derived segment slice preserved from the Embree baseline.",
    ),
    EvaluationEntry(
        case_id="lsi_county_tiled_x8",
        workload="lsi",
        dataset="derived/br_county_subset_segments_tiled_x8",
        title="LSI county tiled x8",
        category="derived",
        provenance="Derived by tiling the checked-in county subset segment view eight times with deterministic offsets.",
        scale_hint=24,
        description="Larger Embree-only local stress case derived from the county subset fixture.",
    ),
    EvaluationEntry(
        case_id="pip_authored_minimal",
        workload="pip",
        dataset="authored_pip_minimal",
        title="PIP authored minimal",
        category="authored",
        provenance="Hand-authored point-in-polygon example stored in baseline_runner.",
        scale_hint=2,
        description="Small sanity-check point-in-polygon case.",
    ),
    EvaluationEntry(
        case_id="pip_county_polygons",
        workload="pip",
        dataset="tests/fixtures/rayjoin/br_county_subset.cdb",
        title="PIP county subset polygons",
        category="fixture",
        provenance="Checked-in county subset fixture converted to probe points and deterministic chain-derived polygons.",
        scale_hint=6,
        description="Fixture-based point-in-polygon benchmark on county-derived polygon views.",
    ),
    EvaluationEntry(
        case_id="pip_county_tiled_x8",
        workload="pip",
        dataset="derived/br_county_subset_polygons_tiled_x8",
        title="PIP county tiled x8",
        category="derived",
        provenance="Derived by tiling county subset probe points and chain-derived polygons eight times.",
        scale_hint=24,
        description="Larger local point-in-polygon case derived from public RayJoin-aligned fixture data.",
    ),
    EvaluationEntry(
        case_id="overlay_authored_minimal",
        workload="overlay",
        dataset="authored_overlay_minimal",
        title="Overlay authored minimal",
        category="authored",
        provenance="Hand-authored overlay seed example stored in baseline_runner.",
        scale_hint=2,
        description="Small compositional overlay sanity check.",
    ),
    EvaluationEntry(
        case_id="overlay_county_soil_fixture",
        workload="overlay",
        dataset="tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb",
        title="Overlay county/soil fixture",
        category="fixture",
        provenance="Checked-in county and soil subset fixtures converted to deterministic chain-derived polygons.",
        scale_hint=4,
        description="Fixture-based overlay seed generation over county and soil subsets.",
    ),
    EvaluationEntry(
        case_id="overlay_county_soil_tiled_x8",
        workload="overlay",
        dataset="derived/br_county_soil_polygons_tiled_x8",
        title="Overlay county/soil tiled x8",
        category="derived",
        provenance="Derived by tiling county and soil chain-derived polygon inputs eight times with fixed offsets.",
        scale_hint=16,
        description="Larger local overlay seed case derived from the public RayJoin-aligned fixtures.",
    ),
    EvaluationEntry(
        case_id="ray_authored_minimal",
        workload="ray_tri_hitcount",
        dataset="authored_ray_tri_minimal",
        title="Ray/Tri authored minimal",
        category="authored",
        provenance="Hand-authored ray-vs-triangle example stored in baseline_runner.",
        scale_hint=2,
        description="Small sanity-check ray hit-count case.",
    ),
    EvaluationEntry(
        case_id="ray_synthetic_small",
        workload="ray_tri_hitcount",
        dataset="examples/rtdl_ray_tri_hitcount.py synthetic random generators",
        title="Ray/Tri synthetic small",
        category="synthetic",
        provenance="Canonical example helper generators with fixed seeds.",
        scale_hint=12,
        description="Baseline random ray/triangle case from the canonical example helpers.",
    ),
    EvaluationEntry(
        case_id="ray_synthetic_medium",
        workload="ray_tri_hitcount",
        dataset="synthetic/ray_tri_medium",
        title="Ray/Tri synthetic medium",
        category="synthetic",
        provenance="Medium-sized deterministic synthetic ray/triangle set from the canonical helper generators.",
        scale_hint=48,
        description="Medium local ray query benchmark with deterministic seeds.",
    ),
    EvaluationEntry(
        case_id="ray_synthetic_large",
        workload="ray_tri_hitcount",
        dataset="synthetic/ray_tri_large",
        title="Ray/Tri synthetic large",
        category="synthetic",
        provenance="Large deterministic synthetic ray/triangle set from the canonical helper generators.",
        scale_hint=192,
        description="Largest local ray query benchmark in the Embree evaluation matrix.",
    ),
)


def evaluation_entries(workloads: tuple[str, ...] | None = None) -> tuple[EvaluationEntry, ...]:
    if workloads is None:
        return EMBREE_EVALUATION_MATRIX
    wanted = set(workloads)
    return tuple(entry for entry in EMBREE_EVALUATION_MATRIX if entry.workload in wanted)
