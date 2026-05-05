from __future__ import annotations

from typing import Any

from .db_primitives import sales_risk_primitive_contract
from .graph_visibility_primitives import visibility_edges_primitive_contract
from .polygon_primitives import polygon_jaccard_diagnostic_contract
from .polygon_primitives import polygon_pair_primitive_contract
from .primitive_contract_schema import validate_primitive_contract


ACTIVE_V1_4_BACKENDS = ("embree", "optix")
FROZEN_BEFORE_V2_1_BACKENDS = ("vulkan", "hiprt", "apple_rt")


def v1_4_primitive_contract_inventory() -> tuple[dict[str, Any], ...]:
    """Return the v1.4 primitive contract inventory for supported app rows."""
    contracts: list[dict[str, Any]] = []
    for backend in ACTIVE_V1_4_BACKENDS:
        contracts.extend(
            (
                visibility_edges_primitive_contract(
                    backend=backend,
                    output_mode="summary",
                    prepared_summary=backend == "optix",
                ),
                sales_risk_primitive_contract(
                    backend=backend,
                    output_mode="compact_summary",
                    materialization_free=True,
                ),
                polygon_pair_primitive_contract(
                    backend=backend,
                    output_mode="summary",
                    candidate_row_count=2,
                ),
                polygon_jaccard_diagnostic_contract(
                    backend=backend,
                    output_mode="summary",
                    candidate_row_count=2,
                ),
            )
        )
    for backend in FROZEN_BEFORE_V2_1_BACKENDS:
        contracts.extend(
            (
                visibility_edges_primitive_contract(
                    backend=backend,
                    output_mode="summary",
                    prepared_summary=False,
                ),
                sales_risk_primitive_contract(
                    backend=backend,
                    output_mode="compact_summary",
                    materialization_free=True,
                ),
                polygon_pair_primitive_contract(
                    backend=backend,
                    output_mode="summary",
                    candidate_row_count=2,
                ),
                polygon_jaccard_diagnostic_contract(
                    backend=backend,
                    output_mode="summary",
                    candidate_row_count=2,
                ),
            )
        )
    return tuple(contracts)


def validate_v1_4_primitive_contract_inventory() -> tuple[dict[str, Any], ...]:
    contracts = v1_4_primitive_contract_inventory()
    for contract in contracts:
        validate_primitive_contract(contract)
    return contracts
