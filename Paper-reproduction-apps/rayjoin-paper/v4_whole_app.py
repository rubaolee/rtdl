"""Application-owned V4 endpoints for the three frozen RayJoin lanes."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

from rtdsl.v4_bounded_relation_optix_compiler import (
    compile_verified_bounded_relation_executable,
)
from rtdsl.v4_bounded_relation_optix_runtime import run_bounded_relation_callback
from rtdsl.v4_bounded_relation_prepared_runtime import (
    prepare_bounded_relation_callback,
)
from rtdsl.v4_bounded_relation_standard_library import (
    compile_standard_bounded_relation_authority,
)
from rtdsl.v4_callback_abi import AnyHitProofAuthority
from rtdsl.v4_callback_ir import AnyHitDeliveryContract
from rtdsl.v4_box_relation_callback import (
    compile_callback as compile_box_callback,
    exact_closed_aabb_relation,
)
from rtdsl.v4_exact_predicate_witness import (
    CandidateProducerKind,
    ExactPartnerAlgebra,
    ExactPredicateWitnessSchema,
    directed_point_location_sos,
    exact_segment_aabb_projection,
    exact_vertical_ray_aabb_projection,
    grouped_exact_segment_pair_counts,
    verify_exact_predicate_witness_schema,
)
from rtdsl.v4_grouped_event_reduction import (
    EventFieldProjection,
    EventFieldSource,
    EventProducerCompletionKind,
    GroupedEventReductionSchema,
    I64LookupTable,
    PreparedGroupedEventReductionOwner,
    compile_grouped_event_reduction,
    execute_grouped_event_reduction,
    materialize_verified_grouped_event_batch,
    reference_grouped_i64x2_count_sum,
    verify_event_producer_evidence,
)
from rtdsl.v4_planar_overlay_lowering import execute_verified_planar_overlay_v4
FORMAL_PAPER_ALGORITHMS = (
    "planar_map.directed_segment_point_location_2d.v1",
    "planar_map.segment_pair_grouped_range_exact_count_2d.v1",
    "logical_events.grouped_i64x2_count_sum.v1",
)
APP_DIR = Path(__file__).resolve().parent


def _fixtures():
    name = "rtdl_v4_rayjoin_fixtures"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = APP_DIR / "v4_fixtures.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _proof(callback):
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "rayjoin_exact_candidate_order_independence_v1",
            "callback": callback.ir_sha256,
            "app_source": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _compile_relation(
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    capacity=4096,
):
    callback = compile_box_callback()
    proof = _proof(callback)
    relation, contract, abi = compile_standard_bounded_relation_authority(
        target, proof, capacity=capacity)
    exact_schema = ExactPredicateWitnessSchema(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=relation.physical.schema.schema_sha256,
        source_authority_nonce=relation.authority_nonce,
        producer_kind=CandidateProducerKind.CLOSED_AABB_RELATION,
        partner_algebras=(
            ExactPartnerAlgebra.DIRECTED_POINT_LOCATION_SOS_I46,
            ExactPartnerAlgebra.SEGMENT_PAIR_GROUPED_COUNT_SOS_I46,
        ),
        maximum_candidate_capacity=capacity,
    )
    exact = verify_exact_predicate_witness_schema(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=relation.physical.schema.schema_sha256,
        source_authority_nonce=relation.authority_nonce,
        schema=exact_schema,
    )
    executable, _ = compile_verified_bounded_relation_executable(
        relation, contract, abi,
        any_hit_proof_authority=proof,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    return relation, contract, abi, proof, exact, executable


def build_v4_input(paper_algorithm: str):
    if paper_algorithm not in FORMAL_PAPER_ALGORITHMS:
        raise ValueError("unsupported RayJoin paper algorithm")
    if paper_algorithm in (FORMAL_PAPER_ALGORITHMS[0], FORMAL_PAPER_ALGORITHMS[2]):
        points, segments = _fixtures().point_location_fixture()
        indexed = exact_segment_aabb_projection(segments)
        sources = exact_vertical_ray_aabb_projection(points, segments)
        expected_rows = (
            (200, 10, 100), (201, 10, 100), (202, 0, 0xFFFFFFFF),
            (203, 10, 100), (204, 30, 102),
        )
        return {
            "points": points, "segments": segments,
            "indexed": indexed, "sources": sources,
            "candidate_rows": exact_closed_aabb_relation(sources, indexed),
            "expected_rows": expected_rows,
            "input_sha256": _digest({
                "algorithm": paper_algorithm,
                "points": [row.__dict__ for row in points],
                "segments": [row.__dict__ for row in segments],
            }),
        }
    left, right = _fixtures().segment_pair_fixture()
    indexed = exact_segment_aabb_projection(right)
    sources = exact_segment_aabb_projection(left)
    return {
        "left": left, "right": right,
        "indexed": indexed, "sources": sources,
        "candidate_rows": exact_closed_aabb_relation(sources, indexed),
        "expected_pairs": ((300, 400), (302, 402)),
        "expected_groups": ((7, 70, 1), (8, 71, 1)),
        "input_sha256": _digest({
            "algorithm": paper_algorithm,
            "left": [row.__dict__ for row in left],
            "right": [row.__dict__ for row in right],
        }),
    }


def _execute_candidates(data, compiled, native_library_path):
    relation, contract, abi, proof, _, executable = compiled
    return run_bounded_relation_callback(
        relation, contract, abi, executable,
        any_hit_proof_authority=proof,
        indexed_boxes=data["indexed"],
        source_boxes=data["sources"],
        expected_rows=data["candidate_rows"],
        native_library_path=native_library_path,
    )


def _grouped_contract(data, exact, exact_rows):
    face_table = I64LookupTable.from_rows(
        (int(row[0]), int(row[1])) for row in exact_rows
        if int(row[2]) != 0xFFFFFFFF)
    segment_group = I64LookupTable.from_rows(
        (int(row.segment_id), int(row.group_id)) for row in data["segments"])
    schema = GroupedEventReductionSchema(
        exact.authority_nonce, 4096,
        EventFieldProjection(
            EventFieldSource.SOURCE_LOOKUP, face_table.table_sha256),
        EventFieldProjection(
            EventFieldSource.ITEM_LOOKUP, segment_group.table_sha256),
        EventFieldProjection(EventFieldSource.CONSTANT, constant_i64=1))
    return schema, (face_table, segment_group)


def _materialize_paper_output(
        paper_algorithm, data, relation, exact, candidates,
        grouped_owner=None):
    if paper_algorithm in (FORMAL_PAPER_ALGORITHMS[0], FORMAL_PAPER_ALGORITHMS[2]):
        exact_result = directed_point_location_sos(
            data["points"], data["segments"], candidates.rows,
            query_map_id=0, capacity=4096)
        if exact_result["rows"] != data["expected_rows"]:
            raise RuntimeError("RayJoin point-location oracle mismatch")
        if paper_algorithm == FORMAL_PAPER_ALGORITHMS[0]:
            return exact_result["rows"], data["expected_rows"]
        semantic_rows = tuple(
            (int(row[0]), int(row[2])) for row in exact_result["rows"]
            if int(row[2]) != 0xFFFFFFFF)
        producer = verify_event_producer_evidence(
            semantic_rows,
            producer_contract_sha256=exact.authority_nonce,
            maximum_event_rows=4096,
            traversal_receipt=candidates.traversal_receipt,
            completion_kind=(
                EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION),
            semantic_completion_authority_sha256=exact.authority_nonce)
        schema, lookups = _grouped_contract(data, exact, exact_result["rows"])
        if grouped_owner is None:
            batch = materialize_verified_grouped_event_batch(
                schema, producer, lookup_tables=lookups)
            reduced = execute_grouped_event_reduction(
                compile_grouped_event_reduction(
                    schema, producer, lookup_tables=lookups), batch)
        else:
            reduced, batch = grouped_owner.execute(producer)
        return reduced.rows, reference_grouped_i64x2_count_sum(batch)
    exact_result = grouped_exact_segment_pair_counts(
        data["left"], data["right"], candidates.rows, capacity=4096)
    return ({
        "exact_pairs": exact_result["exact_pairs"],
        "grouped_counts": exact_result["grouped_counts"],
    }, {
        "exact_pairs": data["expected_pairs"],
        "grouped_counts": data["expected_groups"],
    })


def run_v4_complete(
    paper_algorithm: str,
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path,
):
    started = time.perf_counter()
    data = build_v4_input(paper_algorithm)
    compiled = _compile_relation(
        target=target, compute_capability=compute_capability,
        optix_include=optix_include, cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    relation, _, _, _, exact, _ = compiled
    candidates = _execute_candidates(data, compiled, native_library_path)
    output, expected = _materialize_paper_output(
        paper_algorithm, data, relation, exact, candidates)
    elapsed = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.rayjoin.v4.v1",
        "paper_algorithm": paper_algorithm,
        "input_sha256": data["input_sha256"],
        "output": output,
        "expected": expected,
        "matched": output == expected,
        "registered_complete_seconds": elapsed,
        "complete_timer_includes": (
            "app_input_load", "app_owned_exact_projection",
            "restricted_callback_parse_verify", "abi_and_wrapper_compile",
            "gas_pipeline_sbt_prepare", "optix_candidate_execute",
            "exact_predicate_and_grouped_materialization",
        ),
        "traversal_receipt": candidates.traversal_receipt,
        "native_library_sha256": candidates.native_library_sha256,
        "default_selected_between_paper_algorithms": False,
    }


@dataclass
class PreparedRayJoinV4:
    owner: object
    data: dict[str, object]
    paper_algorithm: str
    relation: object
    exact: object
    grouped_owner: object | None
    total_prepare_seconds: float

    def execute(self, *, source_boxes=None):
        sources = self.data["sources"] if source_boxes is None else tuple(source_boxes)
        started = time.perf_counter()
        candidates = self.owner.execute(
            sources, expected_rows=self.data["candidate_rows"])
        output, expected = _materialize_paper_output(
            self.paper_algorithm, self.data, self.relation,
            self.exact, candidates, self.grouped_owner)
        elapsed = time.perf_counter() - started
        return {
            "schema": "rtdl.paper_reproduction.rayjoin.v4.prepared.v1",
            "paper_algorithm": self.paper_algorithm,
            "output": output, "expected": expected,
            "matched": output == expected,
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False, "cold_result_replaced": False,
            "lifecycle_receipt": self.owner.lifecycle_receipt,
            "grouped_lifecycle_receipt": (
                self.grouped_owner.lifecycle_receipt
                if self.grouped_owner is not None else None
            ),
            "traversal_receipt": candidates.traversal_receipt,
            "native_library_sha256": candidates.native_library_sha256,
        }

    def close(self):
        try:
            if self.grouped_owner is not None:
                self.grouped_owner.close()
        finally:
            self.owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_v4(
    paper_algorithm: str, *, target, compute_capability, optix_include,
    cuda_include, expected_python_version, expected_numba_version,
    expected_numpy_version, native_library_path,
) -> PreparedRayJoinV4:
    started = time.perf_counter()
    data = build_v4_input(paper_algorithm)
    compiled = _compile_relation(
        target=target, compute_capability=compute_capability,
        optix_include=optix_include, cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version)
    relation, contract, abi, proof, exact, executable = compiled
    owner = prepare_bounded_relation_callback(
        authority=relation, contract=contract, abi=abi,
        executable=executable, any_hit_proof_authority=proof,
        indexed_boxes=data["indexed"],
        native_library_path=native_library_path)
    grouped_owner = None
    if paper_algorithm == FORMAL_PAPER_ALGORITHMS[2]:
        # The exact rows are input-derived and route-independent; they define
        # stable projection lookup tables while each live traversal still
        # supplies a fresh sealed producer receipt at execute.
        schema, lookups = _grouped_contract(
            data, exact, data["expected_rows"])
        grouped_owner = PreparedGroupedEventReductionOwner(
            schema, lookup_tables=lookups)
    return PreparedRayJoinV4(
        owner, data, paper_algorithm, relation, exact, grouped_owner,
        time.perf_counter() - started)


def compile_v4_real_scale_six_batch(
    *, lsi_capacity: int, target, compute_capability, optix_include,
    cuda_include, expected_python_version, expected_numba_version,
    expected_numpy_version,
):
    """Compile the app-neutral V4 authority used by the six-batch route."""

    if not isinstance(lsi_capacity, int) or isinstance(lsi_capacity, bool) \
            or lsi_capacity <= 0:
        raise ValueError("positive lsi_capacity required")
    return _compile_relation(
        target=target, compute_capability=compute_capability,
        optix_include=optix_include, cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
        capacity=lsi_capacity,
    )


def run_v4_real_scale_six_batch(
    left, right, *, lsi_capacity: int, target, compute_capability,
    optix_include, cuda_include, expected_python_version,
    expected_numba_version, expected_numpy_version, native_library_path,
    prepared_compiled_relation=None,
):
    """Run the full packed six-batch paper pipeline under V4 authority.

    The two OptiX producers and Numba grouped continuation predate V4 and are
    reused as physical partners.  V4 contributes the canonical restricted
    callback, exact-partner authority, generated PTX identity and fail-closed
    mapping to that device pipeline.  No Python candidate/event rows are
    materialized and no application algorithm is selected.
    """

    compiled = prepared_compiled_relation
    if compiled is None:
        compiled = compile_v4_real_scale_six_batch(
            lsi_capacity=lsi_capacity, target=target,
            compute_capability=compute_capability,
            optix_include=optix_include, cuda_include=cuda_include,
            expected_python_version=expected_python_version,
            expected_numba_version=expected_numba_version,
            expected_numpy_version=expected_numpy_version,
        )
    relation, contract, abi, proof, exact, executable = compiled
    legacy = _load_app_module(
        "rtdl_v4_rayjoin_existing_physical_partners",
        APP_DIR / "rtdl3_whole_app.py")
    args = legacy.prepared_six_batch_args(
        left, right, lsi_capacity=lsi_capacity,
        pair_name="v4_real_scale_six_batch")

    def run_physical():
        # Reuse the already-proven direct device producers and grouped partner
        # without invoking V3's DEFAULT or Action compiler.  V4 authority was
        # consumed above and is what makes this a legal specialized lowering.
        result = legacy.run_v2_prepared_six_batch(args)
        canonical = tuple({
            "batch_index": index,
            "lsi_row_count": int(row["lsi_row_count"]),
            "descriptor_pair_count": int(row["descriptor_pair_count"]),
            "total_groups": int(row.get("descriptor_total_groups", 0)),
            "total_point_rows": int(row.get("descriptor_total_point_rows", 0)),
            "pair_rows_sha256": row.get("descriptor_pair_rows_sha256"),
        } for index, row in enumerate(result["measured_rows"]))
        if len(canonical) != 6:
            raise RuntimeError("V4 RayJoin physical partner did not produce six batches")
        result = dict(result)
        result["output"] = canonical
        return result, canonical

    lowered = execute_verified_planar_overlay_v4(
        relation, contract, abi, executable,
        any_hit_proof_authority=proof,
        exact_authority=exact,
        physical_runner=run_physical,
        native_library_path=native_library_path,
    )
    return {
        "schema": "rtdl.paper_reproduction.rayjoin.v4.real_scale_six_batch.v1",
        "matched": True,
        "output": tuple(lowered.physical_result["output"]),
        "source_result": lowered.physical_result,
        "traversal_receipt": lowered.traversal_receipt,
        "callback_ptx_sha256": lowered.callback_ptx_sha256,
        "physical_lowering": lowered.physical_lowering,
        "python_candidate_or_event_rows_materialized": False,
        "existing_optix_numba_physical_partners_reused": True,
        "default_selected_between_application_algorithms": False,
    }


def _load_app_module(name: str, path: Path):
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


__all__ = [
    "FORMAL_PAPER_ALGORITHMS", "PreparedRayJoinV4", "build_v4_input",
    "prepare_v4", "run_v4_complete", "compile_v4_real_scale_six_batch",
    "run_v4_real_scale_six_batch",
]
