"""Frozen application inventory and experiment-level contract definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppSpec:
    app_id: str
    display_name: str
    source_directory: str
    v4_source_sha256: str
    historical_identity: str
    selected_operation: str
    complete_output_contract: str
    lifecycle_support: tuple[str, ...]
    execution_priority: int
    pyoptix_baseline_status: str


APP_SPECS = (
    AppSpec(
        "particle_tracking",
        "Particle Tracking",
        "goal5753-held-out-particle-tracking",
        "e2d26dd9a67025066ca77d1c57f358c34a8e4446a679b32f772a228ee52712a4",
        "exact_historical_hash_and_consumer_binding",
        "one strict-interior closest-face/cell-transition step",
        "5000 ordered U32x3 rows: selected, neighbor, face",
        ("complete", "first_result", "prepared"),
        1,
        "code_ready_gpu_unvalidated_symmetric_full_public_worker",
    ),
    AppSpec(
        "triangle_counting",
        "Graph Triangle Counting",
        "triangle-counting-paper",
        "8ab4f4ad6c5913483633b06e70035a26637bc2b2a0589ce470623504d86e6210",
        "exact_historical_hash_and_consumer_binding",
        "RT-2A1 on an official SNAP graph",
        "one checked U64 triangle count equal to the published dataset oracle",
        ("complete", "first_result", "prepared"),
        1,
        "code_ready_gpu_unvalidated_public_rt_2a1_owner",
    ),
    AppSpec(
        "librts",
        "LibRTS AABB Index Query",
        "librts-paper",
        "2952d38b341525d5b529a4391949df5b1ab59cd463c752f4da4df0823e40b987",
        "exact_historical_hash_and_consumer_binding",
        "point_contains and range_contains count on parks",
        "one checked U64 count per operation",
        ("complete", "first_result", "prepared"),
        1,
        "code_ready_gpu_unvalidated_public_custom_primitive_count_owner",
    ),
    AppSpec(
        "rtnn",
        "RTNN",
        "rtnn-paper",
        "9ac2119998bf787500177ae02a6beba9172f0230a890f7966094b4a888f7f1f1",
        "recovered_candidate_source_not_old_authority",
        "exact multiround distance-window top-k, K=4",
        "ordered query/rank/candidate IDs and float32 squared distances",
        ("complete", "first_result", "prepared"),
        2,
        "multiround_public_pyoptix_owner_missing",
    ),
    AppSpec(
        "x_hd",
        "X-HD",
        "x-hd-paper",
        "7eb1b7b4c994d5d30a87d214a09fbdcc15e97243720b70b196357d554039d2db",
        "recovered_candidate_source_not_old_authority",
        "directed exact max-of-nearest witness",
        "exact witness IDs and float value within the frozen tolerance",
        ("complete", "first_result", "prepared"),
        2,
        "multiround_public_pyoptix_owner_missing",
    ),
    AppSpec(
        "rt_dbscan",
        "RT-DBSCAN",
        "rt-dbscan-paper",
        "8136260817b2e1f4735fd437c603a990c8bab450a441785fa5aebe676547b338",
        "recovered_candidate_source_not_old_authority",
        "bounded radius graph plus component partition",
        "canonical component labels, core flags, and neighbor counts",
        ("complete", "first_result", "prepared"),
        2,
        "radius_graph_and_component_public_pyoptix_owner_missing",
    ),
    AppSpec(
        "raydb",
        "RayDB",
        "raydb-paper",
        "f482f409fbd6cd565d661d8440886835bdc7417e9d934e89f3fad67f664cbc05",
        "recovered_candidate_source_not_old_authority",
        "SSB-SF10 Q1.1 partitioned grouped I64 sum",
        "ordered partition/group I64 sums",
        ("complete", "first_result"),
        2,
        "partitioned_grouped_public_pyoptix_owner_missing",
    ),
    AppSpec(
        "rayjoin",
        "Spatial RayJoin",
        "rayjoin-paper",
        "968365001aa3393e782e9404d9432dd56abf605a450c8bddfd5717d0ff569df5",
        "recovered_candidate_source_not_old_authority",
        "six-batch county/zipcode planar overlay",
        "six ordered batch result tables and complete-session digest",
        ("complete", "first_result", "prepared"),
        2,
        "six_batch_public_pyoptix_owner_missing",
    ),
    AppSpec(
        "rt_barneshut",
        "RT-BarnesHut",
        "rt-barneshut-paper",
        "98c0f922d50d64f07f1b10af2118924a0b69ebe1bb59096c040a8912d915bc61",
        "recovered_candidate_source_not_old_authority",
        "force evaluation over an already-prepared hierarchy",
        "source IDs exact and scalar forces within frozen abs/rel tolerance",
        ("complete", "first_result", "prepared"),
        2,
        "hierarchy_frontier_public_pyoptix_owner_missing",
    ),
)

_BY_ID = {row.app_id: row for row in APP_SPECS}
if len(APP_SPECS) != 9 or len(_BY_ID) != 9:
    raise RuntimeError("V4/PyOptiX experiment must retain exactly nine applications")


def app_spec(app_id: str) -> AppSpec:
    try:
        return _BY_ID[app_id]
    except KeyError as error:
        raise ValueError(f"unknown V4 paper application: {app_id}") from error


__all__ = ["APP_SPECS", "AppSpec", "app_spec"]
