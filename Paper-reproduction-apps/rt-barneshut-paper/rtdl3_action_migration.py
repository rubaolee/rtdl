"""RTDL 3.0 Action applicability audit for the RT-BarnesHut paper app."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile

from rtdsl.action_api import compile_action_source
from rtdsl.action_frontend import ActionFrontendError, RestrictedActionFrontendContract
from rtdsl.action_ir import (
    F64,
    I64,
    ActionField,
    ActionRecordType,
    ActionReductionSpec,
    ActionScalarLiteral,
    DeliveryEnforcement,
    LogicalEventContract,
    PhysicalDelivery,
    ReductionOperator,
)


APP_DIR = Path(__file__).resolve().parent
ROOT = next(parent for parent in APP_DIR.parents if (parent / "src" / "rtdsl").exists())

ACTION_CANDIDATE_SOURCE = """
def action(event, params):
    weighted = event.source_weight * event.target_weight
    contribution = weighted / event.distance_sq
    reduce("scalar_force", contribution)
"""


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def action_candidate_contract() -> RestrictedActionFrontendContract:
    return RestrictedActionFrontendContract(
        event_type=ActionRecordType(
            "aggregate_contribution",
            (
                ActionField("source_id", I64, nonnegative=True),
                ActionField("target_stable_id", I64, nonnegative=True),
                ActionField("source_weight", F64),
                ActionField("target_weight", F64),
                ActionField("distance_sq", F64, nonnegative=True),
            ),
        ),
        parameter_type=ActionRecordType("parameters", ()),
        logical_event=LogicalEventContract(
            key_fields=("source_id", "target_stable_id"),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="aggregate-hierarchy-visit-single-delivery-v1",
        ),
        reductions=(
            ActionReductionSpec(
                "scalar_force",
                ("source_id",),
                F64,
                ReductionOperator.SUM,
                ActionScalarLiteral.from_python(F64, 0.0),
            ),
        ),
    )


def _synthetic_prepared(body_count: int = 64):
    author_reference = _load(
        "goal5595_rtbh_author_reference",
        APP_DIR / "author_contract_reference.py",
    )
    reader = _load(
        "goal5595_rtbh_prepared_reader",
        ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py",
    )
    bodies = author_reference.make_synthetic_bodies(body_count)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "prepared.json"
        author_reference.write_prepared_arrays(path, bodies)
        return reader.read_prepared_arrays_3d(path)


def run_action_applicability_audit() -> dict[str, object]:
    adapter = _load(
        "goal5595_rtbh_aggregate_adapter",
        APP_DIR / "aggregate_hierarchy_adapter.py",
    )
    prepared = _synthetic_prepared()
    existing = adapter.run_generic_aggregate_frontier_numba_parity(prepared)

    frontend_rejection = None
    try:
        compile_action_source(ACTION_CANDIDATE_SOURCE, action_candidate_contract())
    except ActionFrontendError as exc:
        frontend_rejection = {
            "code": exc.issue.code,
            "path": exc.issue.path,
            "message": exc.issue.message,
        }

    if frontend_rejection is None:
        raise AssertionError("inverse-square Action candidate unexpectedly compiled")

    return {
        "schema": "rtdl.research.action.paper_app_pair.rt_barneshut.v1",
        "app": "rt_barneshut",
        "decision": "retain_generic_aggregate_hierarchy_operator__action_migration_no_go",
        "existing_operator": {
            "contract": existing["adapter_contract"],
            "opening": existing["opening"],
            "reducer": existing["reducer"],
            "point_count": existing["point_count"],
            "node_count": existing["node_count"],
            "reference_numba_match": existing["comparison"]["match"],
            "mismatch_count": existing["comparison"]["mismatch_count"],
        },
        "action_candidate_rejection": frontend_rejection,
        "missing_generic_capabilities": (
            "aggregate_hierarchy_event_producer_binding",
            "typed_division_and_float_reduction_order_contract",
        ),
        "would_require_materialized_contribution_events": True,
        "existing_operator_has_non_force_consumer": True,
        "existing_operator_is_app_neutral": True,
        "action_semantics_claimed": False,
        "backend_lowering_claimed": False,
        "runtime_performance_claimed": False,
        "whole_app_migration_claimed": False,
    }
