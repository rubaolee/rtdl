"""Application-owned V4 complete front door for two LibRTS AABB lanes."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

from rtdsl.v4_aabb_relation_count_lowering import (
    AabbCountAlgebra,
    PreparedVerifiedAabbRelationCountV4,
    verify_aabb_relation_count_authority,
)


APP_DIR = Path(__file__).resolve().parent
MIGRATION = APP_DIR / "rtdl3_action_migration.py"
FORMAL_PAPER_ALGORITHMS = (
    "aabb_index.prepared_query_2d.v1",
    "aabb_overlap.filter_bounded_emit_2d.v1",
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_app():
    name = "rtdl_v4_librts_app_adapter"
    if name in sys.modules:
        return sys.modules[name]
    sys.path.insert(0, str(APP_DIR))
    try:
        spec = importlib.util.spec_from_file_location(name, MIGRATION)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load frozen LibRTS adapter")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(APP_DIR))


def build_v4_input(paper_algorithm: str):
    from rtdsl.v4_box_relation_callback import exact_closed_aabb_relation

    if paper_algorithm not in FORMAL_PAPER_ALGORITHMS:
        raise ValueError("unsupported LibRTS paper algorithm")
    app = _load_app()
    boxes = tuple(app.load_boxes(APP_DIR / "data/fixtures/tiny_boxes.wkt"))
    queries = tuple(app.load_boxes(
        APP_DIR / "data/fixtures/tiny_range_queries.wkt"))
    indexed = tuple(
        (float(box.min_x), float(box.min_y), float(box.max_x),
         float(box.max_y), index)
        for index, box in enumerate(boxes)
    )
    sources = tuple(
        (float(box.min_x), float(box.min_y), float(box.max_x),
         float(box.max_y), index)
        for index, box in enumerate(queries)
    )
    threshold = (
        0.0 if paper_algorithm == FORMAL_PAPER_ALGORITHMS[0] else 0.75)
    reference = app.run_reference_boxes(
        boxes, queries, minimum_overlap=threshold)
    if not reference["matched"]:
        raise RuntimeError("LibRTS route-independent reference mismatch")
    expected = exact_closed_aabb_relation(
        sources, indexed, minimum_overlap=threshold)
    if expected != reference["expected_rows"]:
        raise RuntimeError("LibRTS V4 relation contract differs from app oracle")
    return {
        "indexed": indexed,
        "sources": sources,
        "minimum_overlap": threshold,
        "expected_rows": expected,
        "input_sha256": _digest({
            "algorithm": paper_algorithm, "indexed": indexed,
            "sources": sources, "minimum_overlap": threshold,
        }),
    }


def _proof(callback) -> object:
    from rtdsl.v4_callback_abi import AnyHitProofAuthority
    from rtdsl.v4_callback_ir import AnyHitDeliveryContract

    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "librts_closed_aabb_relation_order_independence_v1",
            "callback": callback.ir_sha256,
            "app_source": _sha(Path(__file__)),
            "migration_source": _sha(MIGRATION),
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def run_v4_complete(
    paper_algorithm: str,
    *,
    target,
    compute_capability: tuple[int, int],
    optix_include,
    cuda_include,
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    native_library_path,
):
    from rtdsl.v4_bounded_relation import (
        BoundedRelationEmissionSchema,
        compile_bounded_relation_contract,
        verify_bounded_relation_schema,
    )
    from rtdsl.v4_bounded_relation_optix_compiler import (
        compile_verified_bounded_relation_executable,
    )
    from rtdsl.v4_bounded_relation_optix_runtime import (
        run_bounded_relation_callback,
    )
    from rtdsl.v4_callback_abi import compile_callback_abi
    from rtdsl.v4_box_relation_callback import compile_callback, physical_schema
    from rtdsl.v4_typed_physical_schema import verify_typed_physical_schema

    started = time.perf_counter()
    app_input = build_v4_input(paper_algorithm)
    callback = compile_callback()
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    schema = BoundedRelationEmissionSchema(
        callback.ir_sha256,
        callback.effect_digest,
        physical.schema.schema_sha256,
        capacity=max(1, len(app_input["indexed"]) * len(app_input["sources"])),
        minimum_overlap_f32=app_input["minimum_overlap"],
    )
    authority = verify_bounded_relation_schema(physical, schema)
    proof = _proof(callback)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    contract = compile_bounded_relation_contract(
        authority, abi_sha256=abi.abi_sha256)
    executable, _ = compile_verified_bounded_relation_executable(
        authority, contract, abi,
        any_hit_proof_authority=proof,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    executed = run_bounded_relation_callback(
        authority, contract, abi, executable,
        any_hit_proof_authority=proof,
        indexed_boxes=app_input["indexed"],
        source_boxes=app_input["sources"],
        expected_rows=app_input["expected_rows"],
        native_library_path=native_library_path,
    )
    elapsed = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.librts.v4.v1",
        "paper_algorithm": paper_algorithm,
        "input_sha256": app_input["input_sha256"],
        "output": {"relation_rows": executed.rows},
        "expected": {"relation_rows": app_input["expected_rows"]},
        "matched": executed.rows == app_input["expected_rows"],
        "registered_complete_seconds": elapsed,
        "complete_timer_includes": (
            "wkt_input_load", "app_owned_box_column_lowering",
            "restricted_callback_parse_verify", "abi_and_wrapper_compile",
            "gas_pipeline_sbt_prepare", "optix_execute",
            "bounded_relation_materialization",
        ),
        "traversal_receipt": executed.traversal_receipt,
        "native_library_sha256": executed.native_library_sha256,
        "default_selected_between_paper_algorithms": False,
    }


@dataclass
class PreparedLibRTSV4:
    owner: object
    app_input: dict[str, object]
    paper_algorithm: str
    total_prepare_seconds: float

    def execute(self, *, source_boxes=None):
        sources = self.app_input["sources"] if source_boxes is None else tuple(source_boxes)
        started = time.perf_counter()
        executed = self.owner.execute(
            sources, expected_rows=self.app_input["expected_rows"])
        elapsed = time.perf_counter() - started
        return {
            "schema": "rtdl.paper_reproduction.librts.v4.prepared.v1",
            "paper_algorithm": self.paper_algorithm,
            "output": {"relation_rows": executed.rows},
            "expected": {"relation_rows": self.app_input["expected_rows"]},
            "matched": executed.rows == self.app_input["expected_rows"],
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False, "cold_result_replaced": False,
            "lifecycle_receipt": self.owner.lifecycle_receipt,
            "traversal_receipt": executed.traversal_receipt,
            "native_library_sha256": executed.native_library_sha256,
        }

    def close(self):
        self.owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_v4(
    paper_algorithm: str, *, target, compute_capability, optix_include,
    cuda_include, expected_python_version, expected_numba_version,
    expected_numpy_version, native_library_path,
) -> PreparedLibRTSV4:
    from rtdsl.v4_bounded_relation import (
        BoundedRelationEmissionSchema,
        compile_bounded_relation_contract,
        verify_bounded_relation_schema,
    )
    from rtdsl.v4_bounded_relation_optix_compiler import (
        compile_verified_bounded_relation_executable,
    )
    from rtdsl.v4_bounded_relation_prepared_runtime import (
        prepare_bounded_relation_callback,
    )
    from rtdsl.v4_callback_abi import compile_callback_abi
    from rtdsl.v4_box_relation_callback import compile_callback, physical_schema
    from rtdsl.v4_typed_physical_schema import verify_typed_physical_schema

    started = time.perf_counter()
    app_input = build_v4_input(paper_algorithm)
    callback = compile_callback()
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256,
        capacity=max(1, len(app_input["indexed"]) * len(app_input["sources"])),
        minimum_overlap_f32=app_input["minimum_overlap"])
    authority = verify_bounded_relation_schema(physical, schema)
    proof = _proof(callback)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    contract = compile_bounded_relation_contract(
        authority, abi_sha256=abi.abi_sha256)
    executable, _ = compile_verified_bounded_relation_executable(
        authority, contract, abi, any_hit_proof_authority=proof,
        compute_capability=compute_capability, optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version)
    owner = prepare_bounded_relation_callback(
        authority=authority, contract=contract, abi=abi, executable=executable,
        any_hit_proof_authority=proof, indexed_boxes=app_input["indexed"],
        native_library_path=native_library_path)
    return PreparedLibRTSV4(
        owner, app_input, paper_algorithm, time.perf_counter() - started)


def prepare_v4_real_scale_count(
    *, target, indexed_columns, operation: str, native_library_path,
):
    """Prepare a scalar-count composition without Cartesian row capacity."""

    algebras = {
        "point_contains": AabbCountAlgebra.POINT_CONTAINS,
        "range_contains": AabbCountAlgebra.RANGE_CONTAINS,
    }
    if operation not in algebras:
        raise ValueError("unsupported LibRTS real-scale count operation")
    authority = verify_aabb_relation_count_authority(
        target=target, algebra=algebras[operation])
    return PreparedVerifiedAabbRelationCountV4(
        authority, indexed_columns=indexed_columns,
        native_library_path=native_library_path)


__all__ = [
    "FORMAL_PAPER_ALGORITHMS", "PreparedLibRTSV4", "build_v4_input",
    "prepare_v4", "prepare_v4_real_scale_count", "run_v4_complete",
]
